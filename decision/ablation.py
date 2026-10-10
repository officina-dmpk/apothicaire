#!/usr/bin/env python
"""Relevance ablation of the decision model: does it read the data table? (D-01, step 7; the question of the reviewer Astra)

  python decision/ablation.py [--model decision/models/qwen35-0.8b-d01-v2] [--split heldout_both] [--decider module:function]
                              [--limit N] [--seed 7] [--out-dir DIR]

Three scorings of the same rows with the same decider:
  none         the rows as they are;
  random_conc  the concentration column of the data digest (`state.data.first_rows`, "time,conc") replaced by random values of the same
               magnitude: each value is drawn uniformly between 0 and the largest concentration of the digest, written with 4 significant
               digits; the time column, the header, the row count, the dose sentence and the request are untouched;
  no_table     the `data` key removed from the state (header, first rows, row count); the request, the dose / route / units sentence, the
               notes and the analyses already in the project stay (the analyses decide the options of `compare_pair`).
The gold is not changed: none of the 20 gold labels is computed from a concentration value (they come from the wording, the dose sentence, the turn kind
and the analyses present), so a model that reads only the words keeps its score. What the ablation shows is whether the answers move.
Report per question: accuracy before and after, number of decisions that flip (label different from the unablated run), mean absolute change of
the probability of the label chosen without ablation.

Without --decider, decider_unsloth:decide is used on the model of --model ($D01_MODEL); the transformation itself needs no model (tested).
"""
import argparse, collections, copy, datetime, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
for _p in (AGENT, HERE):
    if _p not in sys.path: sys.path.insert(0, _p)

MODES = ("none", "random_conc", "no_table")


def _number(text):
    try: return float(text)
    except (TypeError, ValueError): return None


def random_concentrations(state, rng):
    """A copy of `state` whose digest rows "time,conc" carry random concentrations: uniform between 0 and the largest concentration of the
    digest, 4 significant digits. A cell that is not a number (a BLQ marker, an empty cell) stays as it is; a state without digest is returned
    unchanged (a copy)."""
    out = copy.deepcopy(state)
    data = out.get("data")
    if not data or not data.get("first_rows"): return out
    cells = [r.split(",") for r in data["first_rows"]]
    values = [_number(c[1]) for c in cells if len(c) > 1]
    top = max([v for v in values if v is not None] or [0.0])
    new_rows = []
    for c in cells:
        if len(c) > 1 and _number(c[1]) is not None:
            c = [c[0], "%.4g" % (rng.uniform(0.0, top) if top > 0 else 0.0)] + c[2:]
        new_rows.append(",".join(c))
    data["first_rows"] = new_rows
    return out


def drop_table(state):
    """A copy of `state` without its `data` key."""
    out = copy.deepcopy(state)
    out.pop("data", None)
    return out


def transform_state(state, mode, rng=None):
    if mode == "none": return copy.deepcopy(state)
    if mode == "random_conc": return random_concentrations(state, rng or random.Random(0))
    if mode == "no_table": return drop_table(state)
    raise ValueError("mode %r not in %s" % (mode, MODES))


def transform_rows(rows, mode, seed=7):
    """Copies of typed-decisions rows with the state changed by `mode`; the questions, the gold and the id are the same. The random draw of a row
    depends on the seed and the row id only (the same rows give the same values whatever the order)."""
    out = []
    for r in rows:
        rng = random.Random("%s:%s" % (seed, r["id"]))
        state = transform_state(json.loads(r["state"]), mode, rng)
        out.append({**r, "state": json.dumps(state, ensure_ascii=False, sort_keys=True)})
    return out


def compare(base, other):
    """Per question {"flips", "n", "acc_base", "acc_other", "mean_dp"} between two result lists of eval_ood.score_rows (same rows, same order)."""
    per = collections.defaultdict(lambda: {"flips": 0, "n": 0, "ok_base": 0, "ok_other": 0, "dp": 0.0})
    for rb, ro in zip(base, other):
        assert rb["id"] == ro["id"]
        for q, g in rb["gold"].items():
            e = per[q]; pb, po = rb["pred"][q], ro["pred"][q]
            e["n"] += 1; e["ok_base"] += pb["label"] == g; e["ok_other"] += po["label"] == g
            e["flips"] += pb["label"] != po["label"]
            e["dp"] += abs(pb["probs"].get(pb["label"], 0.0) - po["probs"].get(pb["label"], 0.0))
    return {q: {"flips": e["flips"], "n": e["n"], "acc_base": e["ok_base"] / e["n"], "acc_other": e["ok_other"] / e["n"],
                "mean_dp": e["dp"] / e["n"]} for q, e in per.items()}


def exact_rows(results):
    return sum(all(r["pred"][q]["label"] == g for q, g in r["gold"].items()) for r in results)


def report(split, n, scored, comparisons, model):
    """Markdown of the ablation."""
    L = ["# Relevance ablation on %s (%d rows), model %s" % (split, n, model), "",
         "`decision/ablation.py`; none = the rows as they are, random_conc = concentrations of the digest replaced by random values of the same magnitude, "
         "no_table = the data key removed from the state. Gold unchanged (no gold label is computed from a concentration value).", "",
         "| mode | decisions right | all 20 right on a row | decisions that flip against `none` |", "|---|---|---|---|"]
    for mode in MODES:
        res = scored[mode]
        ok = sum(r["pred"][q]["label"] == g for r in res for q, g in r["gold"].items()); tot = sum(len(r["gold"]) for r in res)
        flips = "-" if mode == "none" else "%d / %d" % (sum(c["flips"] for c in comparisons[mode].values()), sum(c["n"] for c in comparisons[mode].values()))
        L.append("| %s | %d / %d = %.2f %% | %d / %d | %s |" % (mode, ok, tot, 100 * ok / tot, exact_rows(res), len(res), flips))
    qs = sorted(comparisons["random_conc"])
    L += ["", "Per question: accuracy without ablation, accuracy after, flips (of %d), mean absolute change of the probability of the original label." % n, "",
          "| question | none | random_conc | flips | mean dp | no_table | flips | mean dp |", "|---|---|---|---|---|---|---|---|"]
    for q in qs:
        a, b = comparisons["random_conc"][q], comparisons["no_table"][q]
        L.append("| %s | %.1f %% | %.1f %% | %d | %.4f | %.1f %% | %d | %.4f |" % (q, 100 * a["acc_base"], 100 * a["acc_other"], a["flips"], a["mean_dp"],
                                                                                 100 * b["acc_other"], b["flips"], b["mean_dp"]))
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--model", default=None, help="model folder for decider_unsloth (sets $D01_MODEL)")
    ap.add_argument("--decider", default="decider_unsloth:decide", help="module:function(state, questions) -> answers")
    ap.add_argument("--split", default="heldout_both", help="decision/data/<split>.jsonl or a path")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args(argv)
    if a.model: os.environ["D01_MODEL"] = os.path.abspath(a.model)
    import eval_ood, zero_shot_d1 as z
    path = a.split if os.path.isfile(a.split) else os.path.join(z.DATA, a.split + ".jsonl")
    rows = z.load_rows(path, a.limit)
    decide, name = eval_ood.load_decider(a.decider)
    scored, comparisons = {}, {}
    for mode in MODES:
        scored[mode], _ = eval_ood.score_rows(transform_rows(rows, mode, a.seed), decide)
        print(mode, "done", flush=True)
        if mode != "none": comparisons[mode] = compare(scored["none"], scored[mode])
    out = a.out_dir or os.path.join(z.RUNS, datetime.date.today().isoformat() + "-ablation")
    os.makedirs(out, exist_ok=True)
    stem = "ablation-%s-%s" % (name, os.path.splitext(os.path.basename(path))[0])
    with open(os.path.join(out, stem + ".md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(report(os.path.basename(path), len(rows), scored, comparisons, name))
    with open(os.path.join(out, stem + ".json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"model": name, "split": os.path.basename(path), "seed": a.seed, "comparisons": comparisons,
                   "rows": {m: [{"id": r["id"], "pred": {q: p["label"] for q, p in r["pred"].items()}} for r in scored[m]] for m in MODES}},
                  f, ensure_ascii=False)
    print(open(os.path.join(out, stem + ".md"), encoding="utf-8").read())


if __name__ == "__main__":
    main()
