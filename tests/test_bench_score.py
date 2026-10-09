"""Tests of the benchmark scorer and of the failure taxonomy (bench/score.py) on synthetic answers.
No model, no engine: numbers come from small hand-written tool results."""
import json, os, sys, time, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gate  # noqa: E402
from bench import score  # noqa: E402

def tool_result(**params):
    return json.dumps({"parameters": params})

def findings_of(answer, tool_texts, users=()):
    allowed = gate.allowed_numbers(tool_texts, users)
    return gate.check(answer, allowed=allowed)["findings"], allowed

class TestMatching(unittest.TestCase):
    def test_value_found_with_the_gate_rounding_rule(self):
        self.assertTrue(score.find_value("Cmax = 8150 ng/mL", 8150.0))
        self.assertTrue(score.find_value("Cmax = 8,15 µg/mL", 8.15))
        self.assertTrue(score.find_value("le pourcentage extrapolé est 3,37 %", 3.3746))
        self.assertTrue(score.find_value("environ 3,4 %", 3.3746))           # 2 digits written: 3.3746 -> 3.4
        self.assertFalse(score.find_value("3,5 %", 3.3746))
        self.assertFalse(score.find_value("Cmax = 8151", 8150.0))           # 4 digits written, the 4th is wrong
        self.assertTrue(score.find_value("Tmax = 2 h", 2.0))
        self.assertFalse(score.find_value("rien", 2.0))
        self.assertTrue(score.find_value("t1/2 = 1,2e-3 h", 0.00123))      # scientific notation

    def test_forbidden_needs_three_digits(self):
        e = {"must_not": [{"label": "CL x1000", "value": 27.1828}]}
        self.assertEqual(score.score_turn("CL/F = 27,2 L/h", e)["forbidden"], ["CL x1000"])
        self.assertEqual(score.score_turn("CL/F = 27 L/h", e)["forbidden"], [])      # 2 digits: could be chance
        self.assertEqual(score.score_turn("CL/F = 0,00271828", e)["forbidden"], [])

    def test_score_turn_must_words_and_new_numbers(self):
        e = {"must": [{"label": "Cmax", "value": 8150.0}, {"label": "Tmax", "value": 2.0}],
             "words": [{"label": "unit", "pattern": r"ng/mL"}]}
        s = score.score_turn("Cmax = 8150 ng/mL à Tmax = 2 h", e)
        self.assertTrue(s["correct"]); self.assertEqual(s["fraction"], 1.0)
        s = score.score_turn("Cmax = 8150 mg/L", e)
        self.assertFalse(s["correct"]); self.assertEqual(s["missing"], ["Tmax"]); self.assertEqual(s["words_missing"], ["unit"])
        self.assertAlmostEqual(s["fraction"], 0.5)
        na = {"words": [{"label": "n/a", "pattern": r"pas calculé"}], "no_new_numbers": True}
        self.assertTrue(score.score_turn("C0 n'est pas calculé pour cette voie.", na, 0)["correct"])
        self.assertFalse(score.score_turn("C0 n'est pas calculé pour cette voie.", na, 2)["correct"])   # a number made up
        self.assertFalse(score.score_turn("C0 vaut 12.", na, 0)["correct"])                              # no 'not available'

    def test_empty_expectation_is_correct(self):
        self.assertTrue(score.score_turn("bonjour", {})["correct"])

class TestTaxonomy(unittest.TestCase):
    def setUp(self):
        self.tool = [tool_result(**{"cl.obs": 0.00271828, "auclast": 100.0, "auclast.alt": 96.5, "aucpext.obs": 5.23, "half.life": 3.1})]

    def cls(self, answer, kind=None, users=()):
        f, allowed = findings_of(answer, self.tool, users)
        self.assertEqual(len(f), 1, (answer, f))
        return score.classify(f[0], allowed, kind)

    def test_unit_conversion(self):
        self.assertEqual(self.cls("CL/F = 27,1828 L/h"), "unit_conversion")           # x 10^4
        self.assertEqual(self.cls("CL/F = 2,71828 L/h"), "unit_conversion")            # x 10^3
        self.assertEqual(self.cls("t1/2 = 186,0 min"), "unit_conversion")              # 3.1 h x 60 (4 digits)
        self.assertEqual(self.cls("CL/F = 163,097 mL/min"), "unit_conversion")         # x 60000

    def test_arithmetic(self):
        self.assertEqual(self.cls("la différence est de 3,500"), "arithmetic")         # 100.0 - 96.5
        self.assertEqual(self.cls("le rapport est de 0,5927"), "arithmetic")           # 3.1 / 5.23
        self.assertEqual(self.cls("soit une baisse de 3,500 %"), "arithmetic")
        self.assertEqual(self.cls("la somme vaut 196,5"), "arithmetic")                # 100 + 96.5
        self.assertNotEqual(self.cls("la différence est de 3,50"), "arithmetic")       # 3 digits: chance, not claimed

    def test_two_digits_are_not_called_a_conversion(self):
        # with 2 digits a power-of-ten coincidence is chance, not evidence
        self.assertNotEqual(self.cls("CL/F = 27 L/h"), "unit_conversion")
        self.assertEqual(self.cls("CL/F = 2718,28 mL/h"), "unit_conversion")           # x 10^6, 6 digits

    def test_ratio_that_is_also_a_power_of_ten_is_a_conversion(self):
        # 0.965 = 96.5 / 100 is a ratio of two allowed numbers AND an allowed number times 10^-2: the rule order says conversion
        self.assertEqual(self.cls("le rapport est de 0,965"), "unit_conversion")

    def test_baseline_of_random_numbers(self):
        """The rules fire by chance on random 3-digit numbers: the baseline measures how often, per class."""
        f, allowed = findings_of("rien 1", self.tool)
        base = score.chance_baseline(allowed, n=60, seed=1)
        self.assertEqual(sum(base.values()), 60); self.assertTrue(set(base) <= set(score.CLASSES))
        self.assertEqual(base, score.chance_baseline(allowed, n=60, seed=1))          # deterministic

    def test_unlabelled_misread(self):
        self.assertEqual(self.cls("le pourcentage extrapolé est 5,28 %"), "unlabelled_misread")   # 5.23 copied wrongly (+1 %)
        self.assertEqual(self.cls("le pourcentage extrapolé est 5,73 %"), "unlabelled_misread")   # one digit changed

    def test_recall_error_and_other(self):
        self.assertEqual(self.cls("la dose était de 450", kind="recall"), "recall_error")
        self.assertEqual(self.cls("la valeur est 777,7"), "other")

    def test_classify_all_and_speed_with_a_large_allowed_set(self):
        many = tool_result(**{f"p{i}": 1.01 * (i + 1) ** 1.3 for i in range(300)})
        f, allowed = findings_of("la valeur est 1234,56 et aussi 0,0987", [many])
        t0 = time.time(); out = score.classify_all(f, allowed)
        self.assertEqual(len(out), 2); self.assertTrue(set(out) <= set(score.CLASSES))
        self.assertLess(time.time() - t0, 15)

if __name__ == "__main__":
    unittest.main()
