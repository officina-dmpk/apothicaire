#!/usr/bin/env python
"""Tables of a model's predictions on a set of rows: accuracy per question next to the best constant and the reviewer's rules, complete vectors (D-01, step 7).

  python decision/set_tables.py --results decision/runs/<run>/unsloth-<model>-<set>-cuda.json --rows decision/data/<set>.jsonl [--out FILE]

`--results` is the JSON written by decision/predict_unsloth.py (one entry per row: gold, label and probabilities of each question), `--rows` the typed-decisions
file it was run on. The reviewer's rules (decision/ood/rules_decider.py, written from the generator's regexes, `asked_<parameter>` always false) are run on the same rows
with eval_ood.score_rows. The best constant is the most frequent gold label of each question on these rows (an upper bound for any constant).
Output: markdown, one table with the 20 questions and one compact table (the 14 `asked_<parameter>` questions averaged), plus the complete vectors (rows whose 20 labels are all right).
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.dirname(HERE), HERE, os.path.join(HERE, "ood")):
    if _p not in sys.path: sys.path.insert(0, _p)
import zero_shot_d1 as z  # noqa: E402

COMPACT = ("analysis", "route", "auc_method", "dose_has_unit", "is_not_available", "compare_pair")


def rules_results(rows):
    """eval_ood.score_rows results of the reviewer's rules on typed-decisions rows."""
    import eval_ood, rules_decider
    return eval_ood.score_rows(rows, rules_decider.decide)[0]


def exact(results):
    """(rows with all labels right, rows)."""
    return sum(all(r["pred"][q]["label"] == g for q, g in r["gold"].items()) for r in results), len(results)


def tables(results, rules=None):
    """Markdown: the 20-question table, the compact table and the complete vectors. `rules` are results on the same rows (None: no rules column)."""
    per, tot = z.accuracy(results); maj = z.majority(results)
    rper, rtot = z.accuracy(rules) if rules else ({}, None)
    maj_tot = (sum(v[0] for v in maj.values()), sum(v[1] for v in maj.values()))
    head = ["question", "model", "best constant"] + (["reviewer's rules"] if rules else [])
    def line(name, a, m, r): return [name, z.pct(*a), z.pct(*m)] + ([z.pct(*r)] if rules else [])
    full = [line(q, per[q], maj[q], rper.get(q)) for q in sorted(per)] + [line("**all 20, per decision**", tot, maj_tot, rtot)]
    asked = [q for q in per if q.startswith("asked_")]
    def mean(d, qs): return (sum(d[q][0] for q in qs), sum(d[q][1] for q in qs))
    compact = [line(q, per[q], maj[q], rper.get(q)) for q in COMPACT if q in per]
    if asked: compact.append(line("`asked_<parameter>` (%d questions pooled)" % len(asked), mean(per, asked), mean(maj, asked), mean(rper, asked) if rules else None))
    def macro7(d):
        vals = [d[q][0] / d[q][1] for q in COMPACT if q in d]
        if asked: vals.append(mean(d, asked)[0] / mean(d, asked)[1])
        return sum(vals) / len(vals)
    compact.append(["macro-average of the seven", "%.1f %%" % (100 * macro7(per)), "%.1f %%" % (100 * macro7(maj))] + (["%.1f %%" % (100 * macro7(rper))] if rules else []))
    compact.append(line("**all 20, per decision**", tot, maj_tot, rtot))
    ex, n = exact(results)
    out = ["### Accuracy per question (%d rows)" % n, "", z.md_table(head, compact), "", "### Complete vectors", "",
           "All 20 labels right: model %d / %d = %.1f %%" % (ex, n, 100 * ex / n) +
           ("; reviewer's rules %d / %d = %.1f %%" % (exact(rules)[0], n, 100 * exact(rules)[0] / n) if rules else "") + ".", "",
           "### All 20 questions", "", z.md_table(head, full)]
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--results", required=True)
    ap.add_argument("--rows", required=True)
    ap.add_argument("--no-rules", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    with open(a.results, encoding="utf-8") as f: run = json.load(f)
    results = run["rows"]
    rows = z.load_rows(a.rows)
    ids = [r["id"] for r in results]
    byid = {r["id"]: r for r in rows}
    text = tables(results, None if a.no_rules else rules_results([byid[i] for i in ids]))
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as f: f.write(text)
    else:
        print(text)


if __name__ == "__main__":
    main()
