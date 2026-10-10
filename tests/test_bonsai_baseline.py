"""Tests of decision/bonsai_baseline.py (subset selection, score shapes, comparison table) on synthetic rows. No model, no GPU."""
import json, os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
sys.path.insert(0, AGENT); sys.path.insert(0, os.path.join(AGENT, "decision"))
import bonsai_baseline as BB  # noqa: E402


def row(i, ex): return {"id": f"r{i}", "factors": json.dumps({"exercise": ex})}


def result(i, gold, pred): return {"id": f"r{i}", "seconds": 1.0, "gold": gold, "pred": {q: {"label": p, "probs": {}} for q, p in pred.items()}}


class SubsetTest(unittest.TestCase):
    def test_first_rows_of_each_exercise_in_file_order(self):
        rows = [row(i, "a" if i % 2 else "b") for i in range(12)]          # a: 1,3,5,7,9,11  b: 0,2,4,6,8,10
        sub = BB.select_subset(rows, 2)
        self.assertEqual([r["id"] for r in sub], ["r0", "r1", "r2", "r3"])
        self.assertEqual(len(BB.select_subset(rows, 100)), 12)

    def test_heldout_file_gives_100_rows_when_present(self):
        if not os.path.isfile(BB.HELDOUT): self.skipTest("decision/data/heldout.jsonl is not generated")
        sub = BB.select_subset(BB.z.load_rows(BB.HELDOUT), 5)
        self.assertEqual(len(sub), 100); self.assertEqual(len({BB.exercise_of(r) for r in sub}), 20)


class TablesTest(unittest.TestCase):
    def setUp(self):
        qs = list(BB.SIX) + ["asked_cmax", "asked_tmax"]
        g = {q: "x" for q in qs}
        self.res = [result(0, g, g), result(1, g, {**g, "route": "y", "asked_cmax": "y"}), result(2, g, {**g, "route": "y"})]
        self.sc = BB.to_scores(self.res)

    def test_scores(self):
        self.assertEqual(self.sc["exact_rows"], 1); self.assertEqual(self.sc["rows"], 3)
        self.assertEqual(self.sc["per_question"]["route"], [1, 3]); self.assertEqual(self.sc["per_question"]["asked_cmax"], [2, 3])
        self.assertEqual(self.sc["constant"]["route"][1], 3)

    def test_groups(self):
        g = BB.group_scores(self.sc)
        self.assertEqual(g["asked"], [5, 6]); self.assertEqual(g["complete"], [1, 3]); self.assertEqual(g["all"], [8 * 3 - 3, 24])
        self.assertAlmostEqual(g["macro"], (5 * 1.0 + 1 / 3 + 5 / 6) / 7)

    def test_scores_json_of_eval_ood_has_the_same_shape(self):
        d = {"rows": 3, "exact_rows": 1, "per_question": {"route": {"correct": 1, "total": 3, "majority": 2 / 3}}}
        s = BB.scores_from_json(d)
        self.assertEqual(s["per_question"]["route"], [1, 3]); self.assertEqual(s["constant"]["route"], [2, 3])

    def test_table_has_a_column_per_system_and_a_row_per_group(self):
        t = BB.comparison_table({"A": self.sc, "B": self.sc})
        lines = t.strip().split("\n")
        self.assertEqual(lines[0].count("|"), 4)                                    # question, A, B
        self.assertEqual(len(lines), 2 + 6 + 4)
        self.assertIn("1/3 = 33.3 %", t); self.assertIn("`route` | 33.3 % | 33.3 %", t)
        self.assertIn("`route`", BB.full_table({"A": self.sc}))


class BreakdownTest(unittest.TestCase):
    def test_turns_and_confusion(self):
        qs = ("analysis", "route", "auc_method", "is_not_available")
        rows = [{"id": "a", "factors": json.dumps({"turn": 1})}, {"id": "b", "factors": json.dumps({"turn": 2})}]
        g = {q: "x" for q in qs}
        res = [result(0, g, {**g, "analysis": "y"}), result(1, g, g)]
        res[0]["id"], res[1]["id"] = "a", "b"
        bt = BB.breakdown_by_turn(rows, res)
        self.assertEqual(bt["first requests"]["analysis"], [0, 1]); self.assertEqual(bt["follow-ups"]["analysis"], [1, 1]); self.assertEqual(bt["first requests"]["rows"], 1)
        self.assertEqual(BB.confusion_cells(res, "analysis"), [("x", "y", 1)]); self.assertEqual(BB.confusion_cells(res, "route"), [])


class RawLogTest(unittest.TestCase):
    def test_rebuild_from_one_call_per_row_and_per_question(self):
        import tempfile
        qs = {"route": {"type": "choice", "instructions": "r", "criteria": {"oral": "o", "unknown": "u"}},
              "asked_cmax": {"type": "noul", "instructions": "c", "criteria": {"false": "No.", "true": "Yes."}}}
        row = {"id": "r0", "state": json.dumps({"request": "q"}), "questions": json.dumps(qs),
               "gold": json.dumps({"route": {"label": "oral"}, "asked_cmax": {"label": "false"}})}
        call = lambda names, raw: {"request": "q", "questions": names, "raw": raw, "seconds": 1.5}
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "row.jsonl")
            with open(p, "w", encoding="utf-8") as f: f.write(json.dumps(call(["route", "asked_cmax"], '{"route": "oral", "asked_cmax": "true"}')) + "\n")
            res = BB.results_from_raw_log([row], p)
            self.assertEqual({q: x["label"] for q, x in res[0]["pred"].items()}, {"route": "oral", "asked_cmax": "true"})
            p2 = os.path.join(tmp, "q.jsonl")
            with open(p2, "w", encoding="utf-8") as f:
                f.write(json.dumps(call(["route"], '{"route": "per os"}')) + "\n" + json.dumps(call(["asked_cmax"], '{"asked_cmax": "false"}')) + "\n")
            res = BB.results_from_raw_log([row], p2)
            self.assertEqual(res[0]["pred"]["route"]["label"], "(outside options)"); self.assertEqual(res[0]["seconds"], 3.0)
            self.assertEqual(BB.to_scores(res)["per_question"]["asked_cmax"], [1, 1])


if __name__ == "__main__":
    unittest.main()
