"""Tests of decision/set_tables.py (tables from stored predictions; no model)."""
import os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "decision"))

import set_tables as st  # noqa: E402


def result(i, analysis_pred, cmax_pred):
    mk = lambda lab, other: {"label": lab, "probs": {lab: 0.9, other: 0.1}}
    return {"id": "r%d" % i, "seconds": 0.1,
            "gold": {"analysis": "nca", "route": "oral", "auc_method": "linear", "dose_has_unit": "true", "is_not_available": "false",
                     "compare_pair": "not_applicable", "asked_cmax": "true", "asked_tmax": "false"},
            "pred": {"analysis": mk(analysis_pred, "x"), "route": mk("oral", "x"), "auc_method": mk("linear", "x"), "dose_has_unit": mk("true", "x"),
                     "is_not_available": mk("false", "x"), "compare_pair": mk("not_applicable", "x"), "asked_cmax": mk(cmax_pred, "x"),
                     "asked_tmax": mk("false", "x")}}


class TestTables(unittest.TestCase):
    def test_exact_rows(self):
        res = [result(1, "nca", "true"), result(2, "none_needed", "true"), result(3, "nca", "false")]
        self.assertEqual(st.exact(res), (1, 3))

    def test_tables_without_rules(self):
        res = [result(1, "nca", "true"), result(2, "none_needed", "true")]
        text = st.tables(res)
        self.assertIn("| analysis | 50.0 % | 100.0 % |", text)               # best constant: the gold is always nca
        self.assertIn("All 20 labels right: model 1 / 2 = 50.0 %.", text)
        self.assertIn("`asked_<parameter>` (2 questions pooled) | 100.0 % |", text)

    def test_tables_with_rules_column(self):
        res = [result(1, "nca", "true")]
        text = st.tables(res, rules=[result(1, "none_needed", "false")])
        self.assertIn("reviewer's rules", text); self.assertIn("rules 0 / 1", text.replace("reviewer's ", ""))


if __name__ == "__main__":
    unittest.main()
