#!/usr/bin/env python
"""The 27B control on the closed questions (D-01, next step 3): run a decider on a fixed subset of rows, and compare it with the trained 0.8B.

  python decision/bonsai_baseline.py run --decider decision.decider_bonsai:decide --out DIR [--rows decision/data/heldout.jsonl] [--per-exercise 5]
  python decision/bonsai_baseline.py compare --out DIR            # tables of DIR/{ood,heldout100}-*.json and the 0.8B / rules / constant references

`run` scores the decider with decision/eval_ood.score_rows (the same function as eval_ood.py, so the same scoring), on the first `per_exercise` rows of
each exercise of the rows file (file order) and writes DIR/<name>.json: per row, the gold, the predicted labels and the seconds.
`compare` reads those files and the references: the trained 0.8B (decision/ood/runs/2026-10-10-qwen35-0.8b/scores.json for the 74 requests; the
per-row predictions of decision/runs/2026-10-09-train-qwen35-0.8b/*-heldout-cuda.json for the held-out subset), the reviewer's rules
(decision/ood/rules_decider.py applied to the same rows) and the best constant per question (chosen with the gold of the rows).
"""
import argparse, collections, hashlib, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
for _p in (AGENT, HERE, os.path.join(HERE, "ood")):
    if _p not in sys.path: sys.path.insert(0, _p)
import eval_ood as E  # noqa: E402
import zero_shot_d1 as z  # noqa: E402

HELDOUT = os.path.join(HERE, "data", "heldout.jsonl")
OOD_ROWS = os.path.join(HERE, "ood", "rows.jsonl")
OOD_SCORES_08B = os.path.join(HERE, "ood", "runs", "2026-10-10-qwen35-0.8b", "scores.json")
HELDOUT_08B = os.path.join(HERE, "runs", "2026-10-09-train-qwen35-0.8b", "unsloth-qwen35-0.8b-d01-merged-heldout-cuda.json")
SIX = ("analysis", "route", "auc_method", "dose_has_unit", "is_not_available", "compare_pair")


def exercise_of(row): return json.loads(row["factors"])["exercise"]


def select_subset(rows, per_exercise=5):
    """The first `per_exercise` rows of each exercise, in file order, exercises in order of first appearance."""
    seen, out = collections.Counter(), []
    for r in rows:
        ex = exercise_of(r)
        if seen[ex] < per_exercise: out.append(r)
        seen[ex] += 1
    return out


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f: h.update(f.read())
    return h.hexdigest()


def to_scores(results):
    """{"rows", "exact_rows", "per_question": {q: [correct, total]}} of results in the score_rows format."""
    per = z.accuracy(results)[0]
    return {"rows": len(results), "exact_rows": sum(E.row_is_exact(r) for r in results), "per_question": {q: list(v) for q, v in per.items()},
            "constant": {q: list(v) for q, v in z.majority(results).items()}}


def scores_from_json(d):
    """Same shape from a scores.json of eval_ood.py."""
    return {"rows": d["rows"], "exact_rows": d["exact_rows"],
            "per_question": {q: [v["correct"], v["total"]] for q, v in d["per_question"].items()},
            "constant": {q: [round(v["majority"] * v["total"]), v["total"]] for q, v in d["per_question"].items()}}


def results_from_run_json(path, ids):
    """Results (score_rows format) of the rows `ids` from a predict_unsloth.py run file ({"rows": [{"id", "seconds", "gold", "pred"}]})."""
    with open(path, encoding="utf-8") as f: rows = {r["id"]: r for r in json.load(f)["rows"]}
    missing = [i for i in ids if i not in rows]
    if missing: raise SystemExit(f"{len(missing)} rows of the subset are not in {path} (first: {missing[0]})")
    return [{"id": i, "seconds": rows[i]["seconds"], "gold": rows[i]["gold"],
             "pred": {q: {"label": p["label"], "probs": p.get("probs", {}), "real_probs": True} for q, p in rows[i]["pred"].items()}} for i in ids]


def results_from_raw_log(rows, log_path):
    """Results (score_rows format) rebuilt from the raw log of decider_bonsai (BONSAI_LOG): the calls are in row order, one per row or one per question.
    The replies are parsed by the decider's own parser; an invalid answer is the label "(outside options)" as in eval_ood.score_rows."""
    import decider_bonsai as B
    with open(log_path, encoding="utf-8") as f: calls = [json.loads(l) for l in f if l.strip()]
    results, i = [], 0
    for r in rows:
        qs, labels, secs = json.loads(r["questions"]), {}, 0.0
        left = set(qs)
        while left:
            c = calls[i]; i += 1
            sub = {q: qs[q] for q in c["questions"]}
            if c["request"] != json.loads(r["state"]).get("request") or not set(sub) <= left:
                raise SystemExit(f"{log_path}: call {i} does not belong to row {r['id']}")
            ans, _ = B.parse(c["raw"], sub)
            labels.update(ans); left -= set(sub); secs += c["seconds"]
        gold = {q: g["label"] for q, g in json.loads(r["gold"]).items()}
        results.append({"id": r["id"], "seconds": secs, "gold": gold,
                        "pred": {q: {"label": labels.get(q, "(outside options)"), "probs": {}} for q in qs}})
    if i != len(calls): raise SystemExit(f"{log_path}: {len(calls) - i} calls left over")
    return results


def rules_results(rows):
    import rules_decider
    return E.score_rows(rows, rules_decider.decide)[0]


# ---------------------------------------------------------------- tables
def group_scores(sc):
    """(six questions, asked mean, macro of the seven, per decision, complete vector) as [correct, total] pairs (macro is a fraction)."""
    pq = sc["per_question"]
    asked = [v for q, v in pq.items() if q.startswith("asked_")]
    asked_pair = [sum(v[0] for v in asked), sum(v[1] for v in asked)]
    six = {q: pq[q] for q in SIX if q in pq}
    seven = [v[0] / v[1] for v in six.values()] + ([asked_pair[0] / asked_pair[1]] if asked else [])
    return {**six, "asked": asked_pair, "macro": sum(seven) / len(seven),
            "all": [sum(v[0] for v in pq.values()), sum(v[1] for v in pq.values())], "complete": [sc["exact_rows"], sc["rows"]]}


def comparison_table(systems):
    """Markdown table; systems: ordered {column name: scores dict (to_scores shape)}. Rows: six questions, asked mean, macro, per decision, complete."""
    g = {n: group_scores(s) for n, s in systems.items()}
    pct = lambda p: "%.1f %%" % (100 * p[0] / p[1])
    rows = [(f"`{q}`", *[pct(g[n][q]) for n in g]) for q in SIX]
    rows.append(("`asked_<parameter>` (mean of 14)", *[pct(g[n]["asked"]) for n in g]))
    rows.append(("macro-average of the seven", *["%.1f %%" % (100 * g[n]["macro"]) for n in g]))
    rows.append(("all 20 questions, per decision", *[pct(g[n]["all"]) for n in g]))
    rows.append(("**all 20 right on a row**", *["%d/%d = %.1f %%" % (g[n]["complete"][0], g[n]["complete"][1], 100 * g[n]["complete"][0] / g[n]["complete"][1]) for n in g]))
    return z.md_table(["question", *systems], rows)


def full_table(systems):
    """Every question, one column per system."""
    qs = list(next(iter(systems.values()))["per_question"])
    return z.md_table(["question", *systems], [(f"`{q}`", *["%.1f %%" % (100 * s["per_question"][q][0] / s["per_question"][q][1]) for s in systems.values()]) for q in qs])


def breakdown_by_turn(rows, results, questions=("analysis", "route", "auc_method", "is_not_available")):
    """{"first requests" | "follow-ups": {question: [correct, total], "rows": n}} of results over rows carrying factors.turn."""
    turn = {r["id"]: json.loads(r["factors"]).get("turn", 1) for r in rows}
    out = {k: {"rows": 0, **{q: [0, 0] for q in questions}} for k in ("first requests", "follow-ups")}
    for res in results:
        k = out["first requests" if turn[res["id"]] == 1 else "follow-ups"]
        k["rows"] += 1
        for q in questions:
            k[q][0] += res["pred"][q]["label"] == res["gold"][q]; k[q][1] += 1
    return out


def confusion_cells(results, question):
    """[(gold, predicted, count)] of the wrong cells of a question, most frequent first."""
    c = collections.Counter((r["gold"][question], r["pred"][question]["label"]) for r in results if r["pred"][question]["label"] != r["gold"][question])
    return [(g, p, n) for (g, p), n in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))]


# ---------------------------------------------------------------- commands
def cmd_run(a):
    rows = z.load_rows(a.rows)
    if a.per_exercise: rows = select_subset(rows, a.per_exercise)
    if a.limit: rows = rows[:a.limit]
    decide, name = E.load_decider(a.decider)
    results, _ = E.score_rows(rows, decide)
    summary = decide.summary() if hasattr(decide, "summary") else {}
    out = {"decider": name, "rows_file": os.path.relpath(a.rows, AGENT), "rows_sha256": sha256(a.rows), "n_rows": len(rows),
           "n_exercises": len({exercise_of(r) for r in rows}), "summary": summary,
           "results": [{"id": r["id"], "seconds": r["seconds"], "gold": r["gold"], "pred": {q: {"label": p["label"]} for q, p in r["pred"].items()}} for r in results]}
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, f"{a.split}-{name}.json")
    with open(path, "w", encoding="utf-8", newline="\n") as f: json.dump(out, f, ensure_ascii=False, indent=1)
    sc = to_scores(results)
    print(name, a.split, "%d/%d decisions" % tuple(group_scores(sc)["all"]), "complete %d/%d" % tuple(group_scores(sc)["complete"]), summary)
    print("written", path)


def _load_run(path):
    with open(path, encoding="utf-8") as f: d = json.load(f)
    return d, [{"id": r["id"], "seconds": r["seconds"], "gold": r["gold"], "pred": {q: {"label": p["label"], "probs": {}} for q, p in r["pred"].items()}} for r in d["results"]]


def cmd_compare(a):
    sections = []
    for split in ("ood", "heldout100"):
        systems, extra = {}, {}
        for variant, col in (("bonsai-27b-row", "27B, one call per row"), ("bonsai-27b-question", "27B, one call per question")):
            p = os.path.join(a.out, f"{split}-{variant}.json")
            if split == "ood":
                log = os.path.join(a.out, "raw", f"ood-{variant.split('-')[-1]}.jsonl")
                if not os.path.isfile(log): continue
                with open(log + ".summary.json", encoding="utf-8") as f: summ = json.load(f)
                res = results_from_raw_log(z.load_rows(OOD_ROWS), log)
                d = {"decider": variant, "summary": {k: v for k, v in summ.items() if k != "invalid"}, "results": res}; systems[col] = to_scores(res); extra[col] = d
            elif os.path.isfile(p):
                d, res = _load_run(p); systems[col] = to_scores(res); extra[col] = d
        if not systems: continue
        ids = [r["id"] for r in res]
        if split == "ood":
            with open(OOD_SCORES_08B, encoding="utf-8") as f: systems["trained 0.8B"] = scores_from_json(json.load(f))
            rows = [r for r in z.load_rows(OOD_ROWS) if r["id"] in set(ids)]
        else:
            systems["trained 0.8B"] = to_scores(results_from_run_json(HELDOUT_08B, ids))
            by = {r["id"]: r for r in z.load_rows(HELDOUT)}
            rows = [by[i] for i in ids]
        systems["reviewer's rules"] = to_scores(rules_results(rows))
        systems["best constant"] = {**next(iter(systems.values())), "per_question": next(iter(systems.values()))["constant"],
                                    "exact_rows": 0}
        # exact rows of the best constant: rows where every question equals its constant
        const = {q: max(collections.Counter(r_gold).items(), key=lambda kv: (kv[1], kv[0]))[0]
                 for q, r_gold in ((q, [json.loads(r["gold"])[q]["label"] for r in rows]) for q in json.loads(rows[0]["gold"]))}
        systems["best constant"]["exact_rows"] = sum(all(json.loads(r["gold"])[q]["label"] == c for q, c in const.items()) for r in rows)
        sections.append((split, systems, extra, rows))
    with open(os.path.join(a.out, "comparison.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({s: {n: {k: v for k, v in sc.items() if k != "constant"} for n, sc in sy.items()} for s, sy, _, _ in sections}, f, indent=1)
    for split, systems, extra, rows in sections:
        print(f"## {split}\n\n" + comparison_table(systems) + "\n")
        print(full_table(systems) + "\n")
        for col, d in extra.items():
            res = d["results"] if split == "ood" else _load_run(os.path.join(a.out, f"{split}-{d['decider']}.json"))[1]
            print(col, "by turn:", json.dumps(breakdown_by_turn(rows, res)), "\n")
            for q in ("analysis", "route", "auc_method", "is_not_available", "compare_pair"): print(" ", col, q, "wrong cells:", confusion_cells(res, q))
            print()
        for col, d in extra.items(): print(col, json.dumps(d["summary"]), "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--decider", required=True); r.add_argument("--out", required=True)
    r.add_argument("--rows", default=HELDOUT); r.add_argument("--per-exercise", type=int, default=5); r.add_argument("--limit", type=int, default=0)
    r.add_argument("--split", default="heldout100")
    c = sub.add_parser("compare"); c.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    {"run": cmd_run, "compare": cmd_compare}[a.cmd](a)


if __name__ == "__main__":
    main()
