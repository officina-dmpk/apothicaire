#!/usr/bin/env python
"""Evaluation of the decision pipeline on out-of-distribution requests (D-01, blind review by an independent expert).

  python decision/eval_ood.py --decider gold|majority|module:function [--date YYYY-MM-DD] [--requests PATH] [--no-run]
                              [--convert-only] [--ids ood-001,ood-002] [--mcp PATH]

Input: decision/ood/requests.jsonl, one JSON object per line (format fixed by decision/review-dsh-brief.md):
  {"id", "exercise", "turn", "prior_analyses": [{"id", "auc_method"[, "kind"]}], "request", "tags": [...],
   "gold": {"analysis", "route", "auc_method", "dose_has_unit", "is_not_available", "compare_pair", "asked": [parameter keys]}}
Exercises are looked up in bench/exercises/, decision/ood/exercises/ and decision/exercises/ (data.csv + meta.json).

1. Conversion. Each line becomes a row of the typed-decisions format, built with the code that builds the training rows
   (make_dataset.make_state, split_first_message, questions_for, gold_choice, gold_noul): the same state, the same 20 questions.
   * turn 1: `request` is the whole text of the user besides the table. Its first line is the dose / route / units sentence
     (user_dose_sentence), its last line is the request of the turn (a one-line text is both), the table follows the first line and
     the scripted BLQ note, if the exercise has one, comes before the last line: the shape of the first message of bench/scripts.py.
     An optional `intro` key of the line replaces the first line.
   * turn > 1: the dose sentence, the table and the notes are those of the scripted first message of the exercise; `request` is the
     message of the turn. The prior analyses are replayed on the engine before the turn (nca_run with the exercise's own arguments).
   * ids of prior analyses are renumbered 2, 3, ... in the order of their ids (the engine numbers analyses that way: the worksheet is 1);
     the gold `compare_pair` follows. The pair options come from questions_for(ids), as in the harness.
   A line that cannot be converted is rejected with its reason (decision/ood/schema_report.md); the rest go to decision/ood/rows.jsonl.
2. Scoring of the decider on the rows (accuracy per question with the always-majority baseline, confusions, per tag, calibration,
   every wrong decision with its request). `gold` must give 100 %, `majority` is the label most frequent in decision/data/train.jsonl.
3. Harness run, one fresh Caladrius session per line, one turn per line: decision/ood/runs/<date>-<decider>/answers.jsonl and
   report.md. Free requests have no oracle, so the report lists what a human must read instead and counts answers and refusals.
"""
import argparse, collections, datetime, importlib, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
for _p in (AGENT, HERE):
    if _p not in sys.path: sys.path.insert(0, _p)
import harness as H  # noqa: E402  (also puts apothicaire on the path)
import make_dataset as md  # noqa: E402
import zero_shot_d1 as z  # noqa: E402
from bench import scripts  # noqa: E402
from bench import make_exercises as mk  # noqa: E402

OOD = os.path.join(HERE, "ood")
REQUESTS = os.path.join(OOD, "requests.jsonl")
ROWS = os.path.join(OOD, "rows.jsonl")
SCHEMA_REPORT = os.path.join(OOD, "schema_report.md")
RUNS = os.path.join(OOD, "runs")
TRAIN = os.path.join(HERE, "data", "train.jsonl")
EXERCISE_ROOTS = (md.BENCH_DIR, os.path.join(OOD, "exercises"), md.EXTRA_DIR)
SPLIT, ID_PREFIX = "ood", "ood"
CONFUSED = ("analysis", "route", "auc_method", "compare_pair", "is_not_available", "dose_has_unit")
ENGINE_FIRST_ID = 2                      # worksheet = 1, analyses are numbered from 2 (decision/make_dataset.py: a1 = 2, a2 = 3)
PRIOR_KINDS = ("nca", "fit_pk1", "fit_pk2")
GOLD_FIELDS = ("analysis", "route", "auc_method", "dose_has_unit", "is_not_available", "compare_pair", "asked")
REQUIRED = ("id", "exercise", "turn", "prior_analyses", "request", "tags", "gold")


class Reject(Exception):
    """A request line that cannot become a row; the message is the reason written in the schema report."""


# ---------------------------------------------------------------- exercises
def find_exercise(ex_id, roots=EXERCISE_ROOTS):
    """(meta, csv text, folder) of an exercise id, searched in the roots in order, or None."""
    for root in roots:
        d = os.path.join(root, ex_id)
        if os.path.isfile(os.path.join(d, "meta.json")) and os.path.isfile(os.path.join(d, "data.csv")):
            meta, csv = mk.load(d)
            return meta, csv, d
    return None


def scripted_first(meta, csv):
    """The scripted first message of an exercise split in its parts (intro, csv, notes, request), or Reject when the exercise folder
    lacks what bench/scripts.first_message needs (route, dose, units, table; not the NCA oracle, which exercises written blind do not have)."""
    try: message = scripts.first_message(meta, csv)
    except Exception as e: raise Reject(f"exercise {meta.get('id')} cannot be scripted by bench/scripts.py ({type(e).__name__}: {e})")
    return md.split_first_message(message)


# ---------------------------------------------------------------- one line -> one row
def _need(cond, why):
    if not cond: raise Reject(why)


def check_line(o):
    """Type and value checks of one parsed line; raises Reject. Returns nothing."""
    _need(isinstance(o, dict), "the line is not a JSON object")
    _need(not (set(REQUIRED) - set(o)), "missing field(s): " + ", ".join(sorted(set(REQUIRED) - set(o))))
    _need(isinstance(o["id"], str) and o["id"].strip(), "`id` must be a non-empty string")
    _need(isinstance(o["exercise"], str) and o["exercise"].strip(), "`exercise` must be a non-empty string")
    _need(isinstance(o["turn"], int) and not isinstance(o["turn"], bool) and o["turn"] >= 1, "`turn` must be an integer >= 1")
    _need(isinstance(o["request"], str) and o["request"].strip(), "`request` must be a non-empty string")
    _need(isinstance(o["tags"], list) and all(isinstance(t, str) and t for t in o["tags"]), "`tags` must be a list of non-empty strings")
    _need(isinstance(o["prior_analyses"], list), "`prior_analyses` must be a list")
    if o["turn"] == 1: _need(not o["prior_analyses"], "turn 1 cannot have prior analyses")
    seen = set()
    for p in o["prior_analyses"]:
        _need(isinstance(p, dict) and isinstance(p.get("id"), int) and not isinstance(p.get("id"), bool),
              "a prior analysis needs an integer `id`")
        _need(p["id"] not in seen, f"duplicate prior analysis id {p['id']}"); seen.add(p["id"])
        kind = p.get("kind", "nca")
        _need(kind in PRIOR_KINDS, f"prior analysis kind {kind!r} not in {PRIOR_KINDS}")
        if kind == "nca": _need(p.get("auc_method") in H.METHODS, f"prior analysis auc_method {p.get('auc_method')!r} not in {H.METHODS}")
    g = o["gold"]
    _need(isinstance(g, dict), "`gold` must be an object")
    _need(not (set(GOLD_FIELDS) - set(g)), "gold is missing: " + ", ".join(sorted(set(GOLD_FIELDS) - set(g))))
    _need(g["analysis"] in md.ANALYSES, f"gold analysis {g['analysis']!r} not in {sorted(md.ANALYSES)}")
    _need(g["route"] in md.ROUTES, f"gold route {g['route']!r} not in {sorted(md.ROUTES)}")
    _need(g["auc_method"] in md.AUC_METHODS, f"gold auc_method {g['auc_method']!r} not in {sorted(md.AUC_METHODS)}")
    for k in ("dose_has_unit", "is_not_available"): _need(isinstance(g[k], bool), f"gold {k} must be a JSON boolean")
    _need(isinstance(g["compare_pair"], str), "gold compare_pair must be a string")
    _need(isinstance(g["asked"], list) and all(isinstance(k, str) for k in g["asked"]), "gold asked must be a list of strings")
    unknown = [k for k in g["asked"] if k not in md.PARAMETERS]
    _need(not unknown, f"gold asked has unknown parameter key(s): {unknown} (allowed: {sorted(md.PARAMETERS)})")


def renumber(prior):
    """([{"id", "kind"[, "auc_method"]}] with ids 2, 3, ... in the order of the original ids, {original id: new id})."""
    out, idmap = [], {}
    for i, p in enumerate(sorted(prior, key=lambda p: p["id"])):
        idmap[p["id"]] = ENGINE_FIRST_ID + i
        kind = p.get("kind", "nca")
        out.append({"id": idmap[p["id"]], "kind": kind, **({"auc_method": p["auc_method"]} if kind == "nca" else {})})
    return out, idmap


def translate_pair(pair, idmap, options):
    """The gold compare_pair in the renumbered ids, in the user's order (a pair is directed: "a+b", a is the reference; 2026-10-10, the
    pair was sorted before and "2+1" became "2+3" instead of "3+2"); Reject when it is not one of the options of the state."""
    if pair in ("not_applicable", "none_available"): new = pair
    else:
        try: a, b = (int(x) for x in pair.split("+"))
        except ValueError: raise Reject(f"gold compare_pair {pair!r} is neither a key 'a+b' nor not_applicable / none_available")
        _need(a in idmap and b in idmap and a != b, f"gold compare_pair {pair!r} names an analysis that is not in prior_analyses {sorted(idmap)}")
        new = f"{idmap[a]}+{idmap[b]}"
    _need(new in options, f"gold compare_pair {pair!r} is outside the options of the state ({sorted(options)})")
    return new


def first_message(o, first, meta, csv):
    """The text of the first user message of a turn-1 line (see the module doc)."""
    lines = [l for l in o["request"].strip().split("\n")]
    head = o.get("intro") or lines[0]
    last = lines[-1]
    mid = lines[1:-1] if len(lines) > 2 else []
    return "\n".join([head, csv.strip(), *first["notes"], *mid, last])


def convert_line(o, find=find_exercise):
    """One parsed line -> item {"row", "message", "first", "prior", "meta", "csv", "exercise_dir", "warnings"}; raises Reject."""
    check_line(o)
    found = find(o["exercise"])
    _need(found is not None, f"unknown exercise {o['exercise']!r} (no folder with data.csv and meta.json)")
    meta, csv, folder = found
    first = scripted_first(meta, csv)
    prior, idmap = renumber(o["prior_analyses"])
    ids = [a["id"] for a in prior]
    qs = md.questions_for(ids)
    g = o["gold"]
    pair = translate_pair(g["compare_pair"], idmap, qs["compare_pair"]["criteria"])
    if o["turn"] == 1:
        message = first_message(o, first, meta, csv)
        parts = md.split_first_message(message)
        _need(parts["csv"], "internal: the first message built from the line has no table")
        intro, data_csv, notes, request = parts["intro"], parts["csv"], parts["notes"], parts["request"]
    else:
        message = o["request"].strip()
        intro, data_csv, notes, request = first["intro"], first["csv"], first["notes"], message
    state = md.make_state(data_csv, intro, list(notes), request, prior)
    gold = {"analysis": md.gold_choice(qs["analysis"]["criteria"], g["analysis"]),
            "route": md.gold_choice(md.ROUTES, g["route"]),
            "auc_method": md.gold_choice(md.AUC_METHODS, g["auc_method"]),
            **{f"asked_{k}": md.gold_noul(k in g["asked"]) for k in md.PARAMETERS},
            "dose_has_unit": md.gold_noul(g["dose_has_unit"]), "is_not_available": md.gold_noul(g["is_not_available"]),
            "compare_pair": md.gold_choice(qs["compare_pair"]["criteria"], pair)}
    assert set(gold) == set(qs)
    warnings = []
    if (g["analysis"] == "compare") != (pair not in ("not_applicable", "none_available")):
        warnings.append("gold analysis and compare_pair disagree (a pair is named only by a compare request)")
    if g["is_not_available"] and not g["asked"]: warnings.append("is_not_available is true but asked is empty (the refusal names no parameter)")
    if idmap != {p["id"]: p["id"] for p in o["prior_analyses"]}:
        warnings.append("prior analysis ids renumbered " + json.dumps({str(k): v for k, v in idmap.items()}) + " (engine numbering)")
    factors = {"exercise": o["exercise"], "family": meta.get("family"), "turn": o["turn"], "request_id": o["id"], "tags": o["tags"],
               "ood": True, "scripted_wording": False, "bench": os.path.normpath(os.path.dirname(folder)) == os.path.normpath(md.BENCH_DIR),
               "route": scripts.kind_of(meta), "n_analyses": len(prior), "prior_ids_original": sorted(idmap),
               "parameters_asked": list(g["asked"]), "blq": bool(meta.get("blq"))}
    agreement = {q: {"argmax_agree": True, "argmax_majority": x["label"], "total_variation": 0.0} for q, x in gold.items()}
    dump = lambda x: json.dumps(x, ensure_ascii=False, sort_keys=True)
    row = {"id": o["id"], "workflow": md.WORKFLOW, "split": SPLIT, "state": dump(state), "questions": dump(qs), "gold": dump(gold),
           "factors": dump(factors), "label_agreement": dump(agreement), "n_questions": len(qs)}
    return {"row": row, "message": message, "first": {"intro": first["intro"], "csv": first["csv"], "notes": first["notes"]},
            "prior": prior, "meta": meta, "csv": csv, "exercise_dir": folder, "warnings": warnings, "tags": o["tags"],
            "request": o["request"], "turn": o["turn"]}


def read_requests(path=REQUESTS, find=find_exercise):
    """(items, rejected) of a requests file. rejected: [{"line", "id", "reason"}]. Ids must be unique."""
    items, rejected, ids = [], [], set()
    with open(path, encoding="utf-8-sig") as f:
        for n, text in enumerate(f, 1):
            if not text.strip(): continue
            o = None
            try:
                try: o = json.loads(text)
                except ValueError as e: raise Reject(f"not valid JSON ({e})")
                item = convert_line(o, find)
                if o["id"] in ids: raise Reject(f"duplicate id {o['id']!r}")
                ids.add(o["id"]); item["line"] = n; items.append(item)
            except Reject as e:
                rejected.append({"line": n, "id": o.get("id") if isinstance(o, dict) else None, "reason": str(e)})
    return items, rejected


def write_rows(items, path=ROWS):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    md.write([it["row"] for it in items], path)


def schema_report(items, rejected, src=REQUESTS):
    L = ["# Schema report of decision/ood/requests.jsonl", "",
         f"Lines converted: {len(items)}. Lines rejected: {len(rejected)}. Converted rows are in `decision/ood/rows.jsonl` "
         f"(typed-decisions format, split `{SPLIT}`, {len(md.questions_for([2, 3]))} questions per row).", ""]
    if rejected:
        L += ["## Rejected lines", "", z.md_table(["line", "id", "reason"], [(r["line"], r["id"] or "-", r["reason"].replace("|", "/")) for r in rejected]), ""]
    warned = [(it["row"]["id"], w) for it in items for w in it["warnings"]]
    if warned: L += ["## Warnings (converted, but worth a look)", "", z.md_table(["id", "warning"], [(i, w.replace("|", "/")) for i, w in warned]), ""]
    by_ex = collections.Counter(it["row"]["id"] and json.loads(it["row"]["factors"])["exercise"] for it in items)
    tags = collections.Counter(t for it in items for t in it["tags"])
    L += ["## Coverage", "", "Rows per exercise: " + ", ".join(f"{k} {v}" for k, v in sorted(by_ex.items())) + ".", "",
          "Rows per tag: " + ", ".join(f"{k} {v}" for k, v in sorted(tags.items())) + ".", ""]
    for q in ("analysis", "route", "auc_method", "compare_pair"):
        c = collections.Counter(json.loads(it["row"]["gold"])[q]["label"] for it in items)
        L.append(f"Gold `{q}`: " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())) + ".")
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------- deciders
def majority_labels(rows):
    """{question: most frequent gold label} over typed-decisions rows (ties: the first label in alphabetical order)."""
    c = collections.defaultdict(collections.Counter)
    for r in rows:
        for q, g in json.loads(r["gold"]).items(): c[q][g["label"]] += 1
    return {q: sorted(v.items(), key=lambda kv: (-kv[1], kv[0]))[0][0] for q, v in c.items()}


def load_train_majority(path=TRAIN, regenerate=True):
    """The majority labels of decision/data/train.jsonl; the dataset is regenerated (make_dataset.py --no-readme) when the file is absent."""
    if not os.path.isfile(path) and regenerate:
        subprocess.run([sys.executable, os.path.join(HERE, "make_dataset.py"), "--no-readme", "--out", os.path.dirname(path)], check=True,
                       stdout=subprocess.DEVNULL)
    return majority_labels(z.load_rows(path))


def majority_decider(labels):
    def decide(state, questions):
        out = {}
        for q, spec in questions.items():
            opts = list(spec["criteria"])
            out[q] = labels[q] if q in labels else opts[0]
        return out
    decide.name = "majority"
    return decide


def gold_labels(row): return {q: g["label"] for q, g in json.loads(row["gold"]).items()}


class RowDecider:
    """A decider that answers from the row being processed (`.row`): the gold labels, or fixed labels (majority)."""
    def __init__(self, name, fixed=None):
        self.name, self.fixed, self.row = name, fixed, None
    def __call__(self, state, questions):
        labels = gold_labels(self.row) if self.fixed is None else self.fixed
        return {q: labels[q] for q in questions if q in labels}


def load_decider(spec, train_path=TRAIN):
    """(function(state, questions) -> answers, name). gold answers from the row being processed (a RowDecider: set `.row` before a call,
    score_rows and run_item do), majority with the labels most frequent in train.jsonl."""
    if spec == "gold": d = RowDecider("gold"); return d, "gold"
    if spec == "majority": d = RowDecider("majority", load_train_majority(train_path)); return d, "majority"
    mod, _, fn = spec.partition(":")
    if not fn: raise SystemExit(f"--decider must be gold, majority or module:function, got {spec!r}")
    f = getattr(importlib.import_module(mod), fn)
    return f, getattr(f, "name", fn)


# ---------------------------------------------------------------- scoring
def score_rows(rows, decide):
    """Results in the format of zero_shot_d1 ({"id", "seconds", "gold", "pred": {q: {"label", "probs"}}}) plus `has_probs`
    (every call of the decider left `decide.last_info` with probabilities). An answer outside the offered options is the label
    "(outside options)", always wrong. A RowDecider has its `.row` set to the row before each call."""
    results, has_probs = [], True
    prev = getattr(decide, "last_info", None)
    for r in rows:
        state, qs = json.loads(r["state"]), json.loads(r["questions"])
        gold = gold_labels(r)
        if isinstance(decide, RowDecider): decide.row = r
        t0 = time.perf_counter()
        raw = decide(state, qs)
        dt = time.perf_counter() - t0
        labels, outside = H.normalize_answers(raw, qs)
        info = getattr(decide, "last_info", None)
        fresh = isinstance(info, dict) and info is not prev and isinstance(info.get("answers"), dict)
        prev = info
        has_probs = has_probs and fresh
        pred = {}
        for q in qs:
            lab = labels[q] if labels[q] is not None else "(outside options)"
            probs = {}
            if fresh and q in info["answers"]: probs = {k: float(v) for k, v in (info["answers"][q].get("probabilities") or {}).items()}
            real = bool(probs)
            probs.setdefault(lab, 0.0 if (labels[q] is None or probs) else 1.0)
            pred[q] = {"label": lab, "probs": probs, "real_probs": real}
        results.append({"id": r["id"], "seconds": dt, "gold": gold, "pred": pred})
    return results, has_probs


def row_is_exact(res): return all(res["pred"][q]["label"] == g for q, g in res["gold"].items())


def per_tag(results, tag_of):
    """{tag: {"rows", "correct", "total", "exact_rows"}} (decisions correct and total over the rows carrying the tag)."""
    out = collections.defaultdict(lambda: {"rows": 0, "correct": 0, "total": 0, "exact_rows": 0})
    for r in results:
        ok = sum(r["pred"][q]["label"] == g for q, g in r["gold"].items())
        for t in tag_of[r["id"]] or ["(no tag)"]:
            e = out[t]; e["rows"] += 1; e["correct"] += ok; e["total"] += len(r["gold"]); e["exact_rows"] += row_is_exact(r)
    return dict(out)


def broken_tags(tags, overall_exact_rate):
    """Tags whose share of fully correct rows is below the overall share (empty when everything is right)."""
    return sorted(t for t, e in tags.items() if e["exact_rows"] / e["rows"] < overall_exact_rate)


def wrong_decisions(results, request_of):
    """[{"id", "question", "gold", "pred", "confidence", "request"}] for every wrong decision."""
    out = []
    for r in results:
        for q, g in r["gold"].items():
            p = r["pred"][q]
            if p["label"] != g: out.append({"id": r["id"], "question": q, "gold": g, "pred": p["label"],
                                            "confidence": p["probs"].get(p["label"]) if p.get("real_probs") else None, "request": request_of[r["id"]]})
    return out


def off_diagonal(results, question):
    """[(gold, predicted, count)] of the wrong cells of the confusion of a question, most frequent first."""
    cm = z.confusion(results, question)
    cells = [(g, p, n) for g, c in cm.items() for p, n in c.items() if p != g]
    return sorted(cells, key=lambda c: (-c[2], c[0], c[1]))


def asked_errors(results):
    """(missed, spurious, total gold true) over the 14 asked_<key> questions."""
    miss = spur = pos = 0
    for r in results:
        for q, g in r["gold"].items():
            if not q.startswith("asked_"): continue
            p = r["pred"][q]["label"]; pos += g == "true"
            miss += g == "true" and p != "true"; spur += g != "true" and p == "true"
    return miss, spur, pos


def scores_json(results, has_probs, baseline, tags, wrong):
    per, tot = z.accuracy(results); maj = z.majority(results)
    base_per = z.accuracy(baseline)[0] if baseline else None
    return {"rows": len(results), "decisions": tot[1], "correct": tot[0], "accuracy": tot[0] / tot[1] if tot[1] else None,
            "exact_rows": sum(row_is_exact(r) for r in results), "has_probs": has_probs,
            "per_question": {q: {"correct": c, "total": t, "accuracy": c / t, "majority": maj[q][0] / maj[q][1],
                                 "train_majority": (base_per[q][0] / base_per[q][1]) if base_per and q in base_per else None}
                             for q, (c, t) in per.items()},
            "per_tag": tags, "wrong_decisions": wrong}


def score_section(results, has_probs, baseline, tag_of, request_of):
    """Markdown of the scoring, and the dict written to scores.json."""
    per, tot = z.accuracy(results); maj = z.majority(results)
    maj_tot = (sum(v[0] for v in maj.values()), sum(v[1] for v in maj.values()))
    base_per, base_tot = (z.accuracy(baseline) if baseline else ({}, None))
    exact = sum(row_is_exact(r) for r in results)
    tags = per_tag(results, tag_of)
    exact_rate = exact / len(results) if results else 0.0
    broke = broken_tags(tags, exact_rate)
    wrong = wrong_decisions(results, request_of)
    L = ["## Scoring on the rows", "",
         f"{len(results)} rows, {tot[1]} decisions: **{z.pct(*tot)}** correct overall; {exact} of {len(results)} rows have all their decisions right "
         f"({z.pct(exact, len(results))}). Always-majority on these rows: {z.pct(*maj_tot)}"
         + (f"; majority learned on train.jsonl: {z.pct(*base_tot)}" if base_tot else "") + ".", "",
         "### Accuracy per question", ""]
    header = ["question", "correct", "total", "accuracy", "always-majority (these rows)", "majority (train.jsonl)"] + (["ECE"] if has_probs else [])
    rows = []
    for q in per:
        row = [q, per[q][0], per[q][1], z.pct(*per[q]), z.pct(*maj[q]), z.pct(*base_per[q]) if q in base_per else "n/a"]
        if has_probs: row.append("%.3f" % z.calibration(results, {q})[1])
        rows.append(row)
    rows.append(["**overall**", tot[0], tot[1], "**%s**" % z.pct(*tot), z.pct(*maj_tot), z.pct(*base_tot) if base_tot else "n/a"]
                + (["%.3f" % z.calibration(results)[1]] if has_probs else []))
    L += [z.md_table(header, rows), "", "### Confusions (wrong cells only: gold -> predicted, count)", ""]
    for q in CONFUSED:
        cells = off_diagonal(results, q)
        L.append(f"- `{q}`: " + ("; ".join(f"{g} -> {p} ({n})" for g, p, n in cells) if cells else "no error") + ".")
    miss, spur, pos = asked_errors(results)
    L += [f"- `asked_<parameter>` (14 questions): {miss} parameters asked and missed (of {pos} asked), {spur} parameters predicted asked that were not.", "",
          "### Accuracy per tag (which kinds of hard requests break)", ""]
    L.append(z.md_table(["tag", "rows", "decisions correct", "accuracy", "rows all right"],
                        [(t, e["rows"], f"{e['correct']}/{e['total']}", z.pct(e["correct"], e["total"]), z.pct(e["exact_rows"], e["rows"]))
                         for t, e in sorted(tags.items(), key=lambda kv: (kv[1]["exact_rows"] / kv[1]["rows"], kv[0]))]))
    L += ["", "Tags that broke (share of fully correct rows below the overall share): " + (", ".join(broke) if broke else "none") + ".", ""]
    L += ["### Calibration (probability of the chosen label vs observed accuracy)", ""]
    if has_probs:
        table, ece = z.calibration(results)
        L.append(z.md_table(["bin", "count", "mean predicted", "observed accuracy"],
                            [("[%.1f, %.1f%s" % (b["lo"], b["hi"], "]" if b["hi"] >= 1 else ")"), b["n"], "%.3f" % b["mean_conf"] if b["n"] else "-",
                              "%.3f" % b["acc"] if b["n"] else "-") for b in table]))
        L.append("\nExpected calibration error: %.3f." % ece)
    else:
        L.append("The decider gives labels without probabilities: no calibration table.")
    L += ["", f"### Wrong decisions ({len(wrong)})", ""]
    if wrong:
        conf = lambda w: "-" if w["confidence"] is None else "%.2f" % w["confidence"]
        L.append(z.md_table(["row", "question", "gold", "predicted", "confidence", "request"],
                            [(w["id"], w["question"], w["gold"], w["pred"], conf(w), w["request"].replace("\n", " / ").replace("|", "/")) for w in wrong]))
    else:
        L.append("None.")
    return "\n".join(L) + "\n", scores_json(results, has_probs, baseline, tags, wrong), broke


# ---------------------------------------------------------------- harness run
def _prefix(template): return template.split("{")[0]


# first match wins: T_NOT_SUPPORTED and T_NOT_WIRED both start "Cette demande (", so the out-of-scope template is tried first on its own
# longer prefix (2026-10-10: it was filed under not-wired)
REFUSAL_PREFIXES = (("no-data", H.T_NO_DATA), ("ask", "Je ne lance pas l'analyse"), ("no-analysis", H.T_NO_ANALYSIS),
                    ("not-supported", H.T_NOT_SUPPORTED.split(":")[0]), ("not-wired", _prefix(H.T_NOT_WIRED)), ("no-parameter", _prefix(H.T_NO_PARAMETER)),
                    ("undecided", _prefix(H.T_UNDECIDED)), ("tool-failed", _prefix(H.T_TOOL_FAILED)),
                    ("which-pair", _prefix(H.T_WHICH_PAIR)))
_NA_MARK = H.T_NOT_AVAILABLE.split("{label}")[1].split("{route}")[0]              # " n'est pas calculé par Caladrius pour cette voie ..."
_NA_MARK_NO_ANALYSIS = H.T_NOT_AVAILABLE_NO_ANALYSIS.split("{label}")[1]


def answer_kind(answer):
    """`answer` for an answer with values, `refusal:<why>` for a template that refuses or asks, `error` is set by the runner."""
    for kind, prefix in REFUSAL_PREFIXES:
        if answer.startswith(prefix): return "refusal:" + kind
    if not answer.startswith("Résultats de Caladrius") and (_NA_MARK in answer or _NA_MARK_NO_ANALYSIS in answer): return "refusal:not-available"
    return "answer"


def expects_refusal(gold):
    """Whether the gold decisions lead the harness to refuse or ask (not to print values): a parameter not available, an NCA with
    no route or no dose unit, a fit or a simulation (not wired), an out-of-scope request (not_supported)."""
    return (gold["is_not_available"] == "true" or (gold["analysis"] == "nca" and (gold["route"] == "unknown" or gold["dose_has_unit"] == "false"))
            or gold["analysis"] in ("fit_pk1", "fit_pk2", "simulate", "not_supported"))


class NotReplayable(Exception): pass


def nca_arguments(meta):
    """{"dose", "route"} of the nca_run calls of an exercise: those of its oracle (ground_truth.nca.linear.nca_run_arguments) when it has
    one, else the dose amount and the route of meta.json (exercises written blind have no oracle; the benchmark ones agree with it)."""
    try: return meta["ground_truth"]["nca"]["linear"]["nca_run_arguments"]
    except KeyError: return {"dose": meta["dose"]["amount"], "route": meta["route"]}


def replay_prior(h, item):
    """Replays the prior analyses of a line on the engine of Harness `h`: the data are imported and nca_run is called with the arguments
    of the exercise's own truth (meta.json) and the AUC method of each analysis. Returns the notes (id mismatches)."""
    prior = item["prior"]
    if not prior: return []
    h.data = dict(item["first"])
    if any(p["kind"] != "nca" for p in prior): raise NotReplayable("a prior analysis is not an NCA (fits cannot be replayed)")
    if h._import() is None: raise NotReplayable("data_import failed: " + h.tool_log[-1]["text"][:200])
    base = nca_arguments(item["meta"])
    notes = []
    for p in prior:
        d = h._run_nca(base["dose"], base["route"], p["auc_method"])
        if d is None: raise NotReplayable("nca_run failed: " + h.tool_log[-1]["text"][:200])
        if d.get("analysis") != p["id"]: notes.append(f"engine numbered a prior analysis {d.get('analysis')}, the row says {p['id']}")
    return notes


def run_item(item, decide, mcp_bin=None):
    """One request through a fresh Harness; returns the record written to answers.jsonl."""
    row = item["row"]; gold = gold_labels(row)
    if isinstance(decide, RowDecider): decide.row = row
    rec = {"id": row["id"], "exercise": json.loads(row["factors"])["exercise"], "turn": item["turn"], "tags": item["tags"],
           "request": item["request"], "prior_analyses": [{k: v for k, v in a.items()} for a in item["prior"]]}
    t0 = time.time()
    h = H.Harness(decide, mcp_bin=mcp_bin)
    try:
        notes = replay_prior(h, item)
        n_log = len(h.tool_log)
        answer, info = h.turn(item["message"])
        rec["answer"] = answer
        rec["answer_kind"] = answer_kind(answer)
        decisions = info["decisions"]
        rec["decisions"] = [{"answers": d["answers"], "outside_options": d["outside_options"],
                             **({"model_info": d["model_info"]} if d.get("model_info") else {})} for d in decisions]
        rec["state_matches_row"] = bool(decisions) and decisions[0]["state"] == json.loads(row["state"])
        first = decisions[0]["answers"] if decisions else {}
        rec["wrong_decisions"] = {q: {"gold": g, "pred": first.get(q)} for q, g in gold.items() if first.get(q) != g}
        rec["harness_notes"] = notes + info["notes"]
        rec["tool_calls"] = [{"name": c["name"], "ok": c["ok"]} for c in h.tool_log]
        rec["new_tool_calls"] = [c["name"] for c in h.tool_log[n_log:]]
        rec["expected_refusal"] = expects_refusal(gold)
    except NotReplayable as e:
        rec.update(answer=None, answer_kind="skipped", error=f"NotReplayable: {e}", expected_refusal=expects_refusal(gold))
    except Exception as e:                                           # recorded, the run continues
        rec.update(answer=None, answer_kind="error", error=f"{type(e).__name__}: {e}", expected_refusal=expects_refusal(gold))
    finally:
        try: h.close()
        except Exception: pass
    rec["wall_s"] = round(time.time() - t0, 3)
    return rec


def to_read(records, broke, cap_per_tag=6):
    """[(record, [reasons])]: what a human must read. A row is listed for each reason: a wrong decision in the run, an answer where a
    refusal was expected (or the reverse), an error / skipped line, a state that differs from the scored row, and (up to `cap_per_tag`
    rows per tag) the rows carrying a tag that broke."""
    out, per_tag_count = [], collections.Counter()
    for r in records:
        why = []
        if r.get("wrong_decisions"): why.append("wrong decision: " + ", ".join(sorted(r["wrong_decisions"])))
        if r["answer_kind"] in ("error", "skipped"): why.append(r["answer_kind"] + ": " + r.get("error", ""))
        elif r["answer_kind"] == "answer" and r["expected_refusal"]: why.append("answered where the gold decisions expect a refusal")
        elif r["answer_kind"].startswith("refusal") and not r["expected_refusal"]: why.append("refused / asked (" + r["answer_kind"][8:] + ") where the gold decisions expect an answer")
        if r.get("state_matches_row") is False: why.append("the harness state differs from the scored row")
        for t in r["tags"]:
            if t in broke and per_tag_count[t] < cap_per_tag: per_tag_count[t] += 1; why.append(f"tag that broke: {t}")
        if why: out.append((r, why))
    return out


def run_section(records, broke):
    kinds = collections.Counter(r["answer_kind"] for r in records)
    n = len(records)
    refusals = sum(v for k, v in kinds.items() if k.startswith("refusal"))
    answers = kinds.get("answer", 0)
    exp = [r for r in records if r["answer_kind"] not in ("error", "skipped")]
    wrong_ref = [r for r in exp if r["answer_kind"] == "answer" and r["expected_refusal"]]
    wrong_ans = [r for r in exp if r["answer_kind"].startswith("refusal") and not r["expected_refusal"]]
    mism = [r["id"] for r in records if r.get("state_matches_row") is False]
    L = ["## Harness run", "",
         f"{n} requests, one fresh Caladrius session each: **{answers} answers with values, {refusals} refusals or questions back**, "
         f"{kinds.get('error', 0)} errors, {kinds.get('skipped', 0)} skipped (prior analyses that cannot be replayed).", "",
         z.md_table(["kind of answer", "count"], sorted(kinds.items())), "",
         "No oracle applies to free requests (bench/score.py reads the scripted turns). Instead:", "",
         f"- answered where the gold decisions expect a refusal or a question back (the dangerous direction): {len(wrong_ref)}"
         + (" (" + ", ".join(r["id"] for r in wrong_ref) + ")" if wrong_ref else ""),
         f"- refused or asked where the gold decisions expect an answer: {len(wrong_ans)}" + (" (" + ", ".join(r["id"] for r in wrong_ans) + ")" if wrong_ans else ""),
         f"- rows whose state, rebuilt by the harness, differs from the scored row: {len(mism)}" + (" (" + ", ".join(mism) + ")" if mism else ""),
         f"- decisions that came back outside the offered options: {sum(len(d['outside_options']) for r in records for d in r.get('decisions', []))}", ""]
    read = to_read(records, broke)
    L += [f"## What a human must read ({len(read)} of {n} requests)", "",
          "Wrong decisions in the run, answers that contradict the gold decisions, errors, and the requests of the tags that broke "
          "(at most 6 per tag). Every other answer is in `answers.jsonl`; a correct decision does not make a correct answer, so read at least a few of them.", ""]
    for r, why in read:
        ans = (r.get("answer") or "").strip()
        L += [f"### {r['id']} ({r['exercise']}, turn {r['turn']}; tags: {', '.join(r['tags']) or '-'})", "",
              "Request: " + r["request"].replace("\n", " / "), "", "Why: " + "; ".join(why), ""]
        for q, d in sorted((r.get("wrong_decisions") or {}).items()): L.append(f"- `{q}`: gold {d['gold']}, predicted {d['pred']}")
        L += ["", "Answer:", "", "```text", ans[:1500] + (" [...]" if len(ans) > 1500 else ""), "```", ""]
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- main
def safe_name(name): return "".join(c if c.isalnum() or c in "-_." else "-" for c in str(name))


def evaluate(items, spec, date, run=True, out_root=RUNS, mcp_bin=None, train_path=TRAIN):
    """Scores and runs the decider `spec` on the converted items; writes the run folder; returns (folder, scores dict, records)."""
    decide, name = load_decider(spec, train_path)
    rows = [it["row"] for it in items]
    tag_of = {it["row"]["id"]: it["tags"] for it in items}
    request_of = {it["row"]["id"]: it["request"] for it in items}
    results, has_probs = score_rows(rows, decide)
    baseline = None
    try: baseline = score_rows(rows, majority_decider(load_train_majority(train_path)))[0]
    except (OSError, subprocess.CalledProcessError): pass
    section, scores, broke = score_section(results, has_probs, baseline, tag_of, request_of)
    folder = os.path.join(out_root, f"{date}-{safe_name(name)}")
    os.makedirs(folder, exist_ok=True)
    head = [f"# Out-of-distribution requests: decider `{name}`, {date}", "",
            f"`decision/eval_ood.py`; {len(items)} requests converted from `decision/ood/requests.jsonl` (schema report: `decision/ood/schema_report.md`).", ""]
    records = []
    body = section
    if run:
        for it in items:
            records.append(run_item(it, decide, mcp_bin))
        with open(os.path.join(folder, "answers.jsonl"), "w", encoding="utf-8", newline="\n") as f:
            for r in records: f.write(json.dumps(r, ensure_ascii=False) + "\n")
        body += "\n" + run_section(records, broke)
        if hasattr(decide, "summary"):
            try: body += "\n## Decision model\n\n" + "\n".join(f"- {k}: {v}" for k, v in decide.summary().items()) + "\n"
            except Exception as e: body += f"\n## Decision model\n\nsummary unavailable ({type(e).__name__}: {e})\n"
    with open(os.path.join(folder, "scores.json"), "w", encoding="utf-8", newline="\n") as f: json.dump(scores, f, ensure_ascii=False, indent=1)
    with open(os.path.join(folder, "report.md"), "w", encoding="utf-8", newline="\n") as f: f.write("\n".join(head) + "\n" + body)
    return folder, scores, records


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--decider", default="gold", help="gold, majority, or module:function with function(state, questions) -> answers")
    ap.add_argument("--requests", default=REQUESTS)
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--ids", default="", help="comma-separated request ids to keep")
    ap.add_argument("--no-run", action="store_true", help="score the decisions only, no harness run (no engine needed)")
    ap.add_argument("--convert-only", action="store_true", help="write rows.jsonl and the schema report, nothing else")
    ap.add_argument("--mcp", default=None, help="path of caladrius-mcp (default: apothicaire.MCP_BIN)")
    a = ap.parse_args(argv)
    if not os.path.isfile(a.requests): raise SystemExit(f"{a.requests} is missing")
    items, rejected = read_requests(a.requests)
    write_rows(items)
    with open(SCHEMA_REPORT, "w", encoding="utf-8", newline="\n") as f: f.write(schema_report(items, rejected, a.requests))
    print(f"converted {len(items)} lines, rejected {len(rejected)}; rows: {ROWS}; schema report: {SCHEMA_REPORT}")
    for r in rejected: print(f"  line {r['line']} ({r['id']}): {r['reason']}")
    if a.convert_only: return
    if a.ids: items = [it for it in items if it["row"]["id"] in a.ids.split(",")]
    if not items: raise SystemExit("no row to evaluate")
    folder, scores, records = evaluate(items, a.decider, a.date, run=not a.no_run, mcp_bin=a.mcp)
    print(f"decider {a.decider}: {scores['correct']}/{scores['decisions']} decisions ({100 * scores['accuracy']:.1f} %), "
          f"{scores['exact_rows']}/{scores['rows']} rows all right")
    if records:
        c = collections.Counter(r["answer_kind"] for r in records)
        print("answers:", dict(c))
    print("report:", os.path.join(folder, "report.md"))


if __name__ == "__main__":
    main()
