"""Tests of the compare turn of the benchmark once the model has the tool `analysis_compare`
(bench/scripts.py: compare_truth, resolve_compare; bench/score.py: compare_usage, parse_compare_row; bench/run_bench.py: resolve_turn).

The rule being tested: when the model called analysis_compare on the linear and the lin-up/log-down analyses, the engine's difference
and percentage are EXPECTED in the answer (read from the tool result, checked against the ground-truth arithmetic of meta.json) and
ALLOWED; every other computed value stays forbidden; without a usable call the static strict rule applies unchanged (the old rule,
which no answer written by the model's own arithmetic can pass). Synthetic exercises only; the real-server test replays the engine
on every committed exercise and needs the built caladrius-mcp (skipped without it).
"""
import copy, json, os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
sys.path.insert(0, AGENT)
import apothicaire  # noqa: E402
from bench import make_exercises as mk, scripts as sc, score, run_bench as rb  # noqa: E402

BUILT = os.path.exists(apothicaire.MCP_BIN)

def exercise(prefix):
    d = next(x for x in mk.list_exercises() if os.path.basename(x).startswith(prefix))
    meta, csv = mk.load(d)
    return meta, csv, sc.build_script(meta, csv)

def fake_nca(aid, method):
    """A stored nca_run record as run_bench.tool_records writes it (the digest the model saw, its first characters)."""
    return {"name": "nca_run", "status": "valid", "args": {"options": {"auc_method": method}},
            "shown": json.dumps({"analysis": aid, "label": "x", "status": "fresh", "options_used": {"auc_method": method}}, separators=(",", ":"))}

def fake_compare(meta, a, b, ref, params=("auclast",), status="valid", tweak=None):
    t = sc.compare_truth(meta, ref); unit = sc.truth_unit(meta, "auclast")
    lin, lud = sc.truth_value(meta, "auclast"), sc.truth_value(meta, "auclast", "lin_up_log_down")
    av, bv = (lin, lud) if ref == "linear" else (lud, lin)
    t = {**t, **(tweak or {})}
    lines = {p: (f"a {av:.6g} {unit} | b {bv:.6g} {unit} | difference {t['difference']:.6g} {unit} | percent {t['percent']:.6g} % | ratio {t['ratio']:.6g}")
             for p in params}
    return {"name": "analysis_compare", "status": status, "args": {"a": a, "b": b, "parameters": list(params)},
            "shown": json.dumps({"a": {"analysis": a}, "b": {"analysis": b}, "subject": "1", "parameters": lines, "not_comparable": {}}, separators=(",", ":"))}

def fmt(v, comma=True):
    s = f"{v:.6g}"
    return s.replace(".", ",") if comma else s

class TestUsage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.meta, cls.csv, cls.script = exercise("ex01")
        cls.prior = [fake_nca(2, "linear")]
        cls.this = [fake_nca(3, "lin_up_log_down")]
        cls.truth = lambda s, ref: sc.compare_truth(s.meta, ref)

    def usage(self, compare, prior=None, this=None):
        return score.compare_usage(prior if prior is not None else self.prior, (this if this is not None else self.this) + compare, truth=self.truth)

    def test_a_usable_call_in_both_orientations(self):
        for a, b, ref in ((2, 3, "linear"), (3, 2, "lin_up_log_down")):
            u = self.usage([fake_compare(self.meta, a, b, ref)])
            self.assertTrue(u["usable"], u); self.assertEqual((u["calls"], u["valid"], u["reference"]), (1, 1, ref))
            t = sc.compare_truth(self.meta, ref)
            for k in ("difference", "percent", "ratio"): self.assertAlmostEqual(u["row"][k], t[k], delta=abs(t[k]) * 5e-6)

    def test_the_orientation_changes_the_percentage_and_the_ratio_not_the_absolute_difference(self):
        lin, lud = sc.compare_truth(self.meta, "linear"), sc.compare_truth(self.meta, "lin_up_log_down")
        self.assertAlmostEqual(lin["difference"], -lud["difference"], places=9)
        self.assertNotAlmostEqual(abs(lin["percent"]), abs(lud["percent"]), places=3)
        self.assertAlmostEqual(lin["ratio"] * lud["ratio"], 1.0, places=9)

    def test_not_usable(self):
        m = self.meta
        self.assertFalse(self.usage([])["usable"]); self.assertEqual(self.usage([])["calls"], 0)
        u = self.usage([fake_compare(m, 2, 3, "linear", status="invalid")]); self.assertEqual((u["calls"], u["valid"], u["usable"]), (1, 0, False))
        self.assertFalse(self.usage([fake_compare(m, 2, 2, "linear")])["usable"])                       # the analysis with itself
        self.assertFalse(self.usage([fake_compare(m, 2, 9, "linear")])["usable"])                       # an unknown analysis
        self.assertFalse(self.usage([fake_compare(m, 2, 3, "linear")], prior=[fake_nca(2, "linear")], this=[fake_nca(3, "linear")])["usable"])   # two linear analyses
        self.assertFalse(self.usage([fake_compare(m, 2, 3, "linear", params=("aucinf.obs",))])["usable"])   # no auclast row
        self.assertFalse(self.usage([fake_compare(m, "x", 3, "linear")])["usable"])                      # not an id

    def test_a_row_that_disagrees_with_the_ground_truth_is_not_trusted(self):
        t = sc.compare_truth(self.meta, "linear")
        u = self.usage([fake_compare(self.meta, 2, 3, "linear", tweak={"percent": t["percent"] * 1.01})])
        self.assertFalse(u["usable"]); self.assertIn("mismatch", u)

    def test_row_parser(self):
        row = score.parse_compare_row('{"parameters":{"cmax":"a 1 | b 1","auclast":"a 148.923 h*mg/L | b 147.235 h*mg/L | difference -1.6883 h*mg/L | percent -1.13367 % | ratio 0.988663"}}')
        self.assertEqual(row, {"a": 148.923, "b": 147.235, "difference": -1.6883, "percent": -1.13367, "ratio": 0.988663})
        self.assertIsNone(score.parse_compare_row('{"parameters":{"auclast":"a 5 h | b 6 h | difference 1 h | not comparable: a is zero"}}'))
        self.assertIsNone(score.parse_compare_row('{"parameters":{"cmax":"a 1"}}'))

class TestRule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.meta, cls.csv, cls.script = exercise("ex01")
        cls.turn = cls.script[6]
        cls.calls = [fake_nca(2, "linear"), fake_nca(3, "lin_up_log_down")]
        cls.lin, cls.lud = sc.truth_value(cls.meta, "auclast"), sc.truth_value(cls.meta, "auclast", "lin_up_log_down")
        cls.unit = sc.truth_unit(cls.meta, "auclast")

    def resolve(self, a=2, b=3, ref="linear"):
        turn, resolved = rb.resolve_turn(self.meta, self.turn, [{"tool_calls": self.calls[:1]}], self.calls[1:] + [fake_compare(self.meta, a, b, ref)])
        return turn, resolved

    def answer(self, ref="linear", extra="", comma=True, sign=-1):
        t = sc.compare_truth(self.meta, ref); u = self.unit.replace("*", "·")
        return "\n".join([f"- AUC(0-tlast) linéaire : {fmt(self.lin, comma)} {u}", f"- AUC(0-tlast) lin-up/log-down : {fmt(self.lud, comma)} {u}",
                          f"- Différence : {fmt(sign * abs(t['difference']), comma)} {u}", f"- Écart relatif : {fmt(sign * abs(t['percent']), comma)} %", extra]).strip()

    def test_without_a_call_the_static_rule_is_unchanged(self):
        turn, resolved = rb.resolve_turn(self.meta, self.turn, [], [])
        self.assertIs(turn, self.turn); self.assertFalse(resolved) if isinstance(resolved, bool) else self.assertEqual(resolved["calls"], 0)
        t = sc.compare_truth(self.meta, "linear")
        r = score.score_turn(self.answer(), self.turn["expect"], 0)           # the engine's numbers, but the model never called the tool
        self.assertFalse(r["correct"]); self.assertTrue(r["forbidden"])
        two_values = f"Linéaire : {fmt(self.lin)} {self.unit}, lin-up/log-down : {fmt(self.lud)} {self.unit}. Caladrius ne calcule pas la différence."
        self.assertTrue(score.score_turn(two_values, self.turn["expect"], 0)["correct"])

    def test_with_a_usable_call_the_engines_numbers_are_expected_and_allowed(self):
        for ref in ("linear", "lin_up_log_down"):
            a, b = (2, 3) if ref == "linear" else (3, 2)
            turn, usage = self.resolve(a, b, ref)
            self.assertTrue(usage["usable"])
            labels = [i["label"] for i in turn["expect"]["must"]]
            self.assertEqual(labels[-2:], ["AUC difference (analysis_compare)", "AUC difference in % (analysis_compare)"])
            t = sc.compare_truth(self.meta, ref)
            self.assertAlmostEqual(turn["expect"]["must"][-2]["value"], abs(t["difference"]), delta=abs(t["difference"]) * 5e-6)
            self.assertAlmostEqual(turn["expect"]["must"][-1]["value"], abs(t["percent"]), delta=abs(t["percent"]) * 5e-6)
            self.assertEqual((turn["expect"]["must"][-2]["unit"], turn["expect"]["must"][-1]["unit"]), (self.unit, "%"))
            r = score.score_turn(self.answer(ref), turn["expect"], 0)
            self.assertTrue(r["correct"], r)
            o = score.oracle_turn(self.answer(ref), turn["expect"], self.meta)
            self.assertTrue(o["correct"], [i for i in o["items"] if not i["ok"]]); self.assertEqual((o["n_items"], o["n_ok"]), (4, 4))
            left = {m["label"].strip() for m in turn["expect"]["must_not"]}
            # the tool's difference, its percentage and (reference linear) its ratio b / a are allowed; the rest stays forbidden
            want = {"AUC difference in % of the " + ("log-down" if ref == "linear" else "linear") + " AUC", "AUC ratio in %"}
            want |= set() if ref == "linear" else {"AUC ratio"}
            self.assertEqual(left, want)

    def test_what_stays_forbidden(self):
        turn, _ = self.resolve(2, 3, "linear")
        other = abs(sc.compare_truth(self.meta, "lin_up_log_down")["percent"])        # the percentage of the OTHER reference: a model computation
        ratio_pct = sc.compare_truth(self.meta, "linear")["ratio"] * 100
        for wrong in (f"{fmt(other)} %", f"{fmt(ratio_pct)} %"):
            r = score.score_turn(self.answer() + f"\nSoit {wrong}", turn["expect"], 0)
            self.assertFalse(r["correct"], wrong); self.assertTrue(r["forbidden"], wrong)
        # the ratio b / a of the tool, written as is, is allowed
        r = score.score_turn(self.answer(extra=f"- Rapport : {fmt(sc.compare_truth(self.meta, 'linear')['ratio'])}"), turn["expect"], 0)
        self.assertTrue(r["correct"], r)
        # a value the gate did not find in a tool result still fails the turn (no_new_numbers)
        self.assertFalse(score.score_turn(self.answer(), turn["expect"], 1)["correct"])

    def test_a_missing_or_wrong_difference_or_percentage_is_incorrect(self):
        turn, _ = self.resolve()
        t = sc.compare_truth(self.meta, "linear"); u = self.unit.replace("*", "·")
        no_numbers = f"- linéaire : {fmt(self.lin)} {u}\n- lin-up/log-down : {fmt(self.lud)} {u}\nLes deux AUC diffèrent peu."
        r = score.score_turn(no_numbers, turn["expect"], 0); self.assertFalse(r["correct"]); self.assertEqual(len(r["missing"]), 2)
        o = score.oracle_turn(no_numbers, turn["expect"], self.meta)
        self.assertEqual([i["class"] for i in o["items"] if not i["ok"]], ["missing_value", "missing_value"])
        wrong = self.answer().replace(fmt(abs(t["difference"])), fmt(abs(t["difference"]) * 1.2))
        self.assertFalse(score.oracle_turn(wrong, turn["expect"], self.meta)["correct"])

    def test_oracle_in_several_styles(self):
        turn, _ = self.resolve()
        t = sc.compare_truth(self.meta, "linear"); u = self.unit.replace("*", "·")
        d, p = fmt(abs(t["difference"])), fmt(abs(t["percent"]))
        styles = {
            "sentence": f"L'AUC linéaire vaut {fmt(self.lin)} {u} et l'AUC lin-up/log-down {fmt(self.lud)} {u}. Elles diffèrent de {d} {u}, soit {p} %.",
            "difference then percentage in one line": f"AUC linéaire = {fmt(self.lin)} {u} ; AUC lin-up/log-down = {fmt(self.lud)} {u} ; différence = {d} {u} ({p} %)",
            "method named in the difference line": f"- linéaire : {fmt(self.lin)} {u}\n- lin-up/log-down : {fmt(self.lud)} {u}\n- Différence (lin-up/log-down − linéaire) : −{d} {u} (−{p} %)",
            "table": f"| Méthode | AUC |\n|---|---|\n| linéaire | {fmt(self.lin)} {u} |\n| lin-up/log-down | {fmt(self.lud)} {u} |\n\nDifférence : {d} {u} ; différence relative : {p} %",
            "decimal point and star": f"Linear: {self.lin:.6g} {self.unit}; lin-up/log-down: {self.lud:.6g} {self.unit}. Difference {t['difference']:.6g} {self.unit} ({t['percent']:.6g} %)."}
        for name, ans in styles.items():
            with self.subTest(style=name):
                o = score.oracle_turn(ans, turn["expect"], self.meta)
                self.assertTrue(o["correct"], [i for i in o["items"] if not i["ok"]])

    def test_a_missing_unit_on_the_percentage_is_reported(self):
        turn, _ = self.resolve()
        t = sc.compare_truth(self.meta, "linear"); u = self.unit.replace("*", "·")
        ans = self.answer().replace(f"{fmt(abs(t['percent']))} %", f"{fmt(abs(t['percent']))}")
        o = score.oracle_turn(ans, turn["expect"], self.meta)
        self.assertEqual([(i["label"], i["class"]) for i in o["items"] if not i["ok"]], [("AUC difference in % (analysis_compare)", "missing_unit")])

    def test_rescore_resolves_from_the_stored_records(self):
        """attach_oracle on stored turns: the compare turn is judged against the resolved rule, the other turns are untouched."""
        recs = []
        for k, st in enumerate(self.script):
            tc = [fake_nca(2, "linear")] if k == 0 else ([fake_nca(3, "lin_up_log_down"), fake_compare(self.meta, 2, 3, "linear")] if k == 6 else [])
            ans = self.answer() if k == 6 else ("pas disponible" if k == 7 else "")
            if st["expect"].get("must") and k != 6:
                ans = "\n".join(f"{i['label']} = {fmt(i['value'])} {i['unit']}" for i in st["expect"]["must"])
            recs.append({"turn": k + 1, "kind": st["kind"], "answer": ans, "tool_calls": tc})
        rec = {"id": self.meta["id"], "turns": recs}
        rb.attach_oracle(rec, self.meta, self.script)
        self.assertEqual(recs[6]["oracle"]["n_items"], 4); self.assertTrue(recs[6]["oracle"]["correct"])
        recs[6]["tool_calls"] = recs[6]["tool_calls"][:1]                          # no compare call: the strict rule, 2 items
        rb.attach_oracle(rec, self.meta, self.script)
        self.assertEqual(recs[6]["oracle"]["n_items"], 2)

    def test_the_report_counts_what_the_model_did(self):
        turn_ok = {"kind": "compare", "compare_tool": {"calls": 2, "valid": 2, "usable": True}, "tool_calls": [{"name": "analysis_compare"}] * 2}
        turn_no = {"kind": "compare", "compare_tool": {"calls": 0, "valid": 0, "usable": False}, "tool_calls": []}
        turn_bad = {"kind": "compare", "compare_tool": {"calls": 1, "valid": 1, "usable": False, "mismatch": {"tool": {}}}, "tool_calls": [{"name": "analysis_compare"}]}
        c = rb.compare_section([{"id": "a", "turns": [turn_ok]}, {"id": "b", "turns": [turn_no]}, {"id": "c", "turns": [turn_bad]}])
        self.assertEqual((c["turns"], c["turns_with_call"], c["calls"], c["valid_calls"], c["turns_usable"]), (3, 2, 3, 3, 1))
        self.assertEqual((c["turns_without_call"], c["turns_row_disagrees_with_truth"], c["analysis_compare_calls_all_turns"]), (["b"], ["c"], 3))

@unittest.skipUnless(BUILT, "caladrius-mcp is not built")
class TestEngineAgainstGroundTruth(unittest.TestCase):
    def test_every_exercise_both_orientations(self):
        """The real engine: data_import, nca_run linear and lin-up/log-down, analysis_compare in both orientations, the digest the model
        sees, parsed back by the benchmark: usable, and equal to the arithmetic of meta.json (compare_truth)."""
        client = apothicaire.MCPClient([apothicaire.MCP_BIN])
        try:
            for d in mk.list_exercises():
                m, csv = mk.load(d); units = {}
                imp = {"name": m["id"], "csv": csv, "columns": m["ground_truth"]["data_import_columns"]}
                ok, text = client.call("data_import", imp); self.assertTrue(ok, text)
                apothicaire.render_tool_result("data_import", ok, text, units)
                ws = json.loads(text)["worksheet"]["id"]; calls, ids = [], {}
                for method in mk.METHODS:
                    ok, text = client.call("nca_run", {"worksheet": ws, **m["ground_truth"]["nca"][method]["nca_run_arguments"]})
                    self.assertTrue(ok, text); ids[method] = json.loads(text)["id"]
                    calls.append({"name": "nca_run", "status": "valid", "args": {}, "shown": apothicaire.render_tool_result("nca_run", ok, text, units)})
                for ref, (a, b) in (("linear", ("linear", "lin_up_log_down")), ("lin_up_log_down", ("lin_up_log_down", "linear"))):
                    args = {"a": ids[a], "b": ids[b], "parameters": ["auclast"]}
                    ok, text = client.call("analysis_compare", args); self.assertTrue(ok, text)
                    rec = {"name": "analysis_compare", "status": "valid", "args": args, "shown": apothicaire.render_tool_result("analysis_compare", ok, text, units)}
                    with self.subTest(ex=m["id"], reference=ref):
                        u = score.compare_usage(calls, [rec], truth=lambda r: sc.compare_truth(m, r))
                        self.assertTrue(u["usable"], u); self.assertEqual(u["reference"], ref)
                        # and the whole path: the resolved turn accepts an answer built from the tool's row
                        turn, resolved = sc.resolve_compare(sc.build_script(m, csv)[6], m, u)
                        self.assertTrue(resolved)
                        unit = sc.truth_unit(m, "auclast").replace("*", "·")
                        ans = (f"- AUC(0-tlast) linéaire : {sc.truth_value(m, 'auclast'):.6g} {unit}\n- AUC(0-tlast) lin-up/log-down : "
                               f"{sc.truth_value(m, 'auclast', 'lin_up_log_down'):.6g} {unit}\n- Différence : {u['row']['difference']:.6g} {unit}\n"
                               f"- Écart relatif : {u['row']['percent']:.6g} %")
                        self.assertTrue(score.score_turn(ans, turn["expect"], 0)["correct"], m["id"])
                        o = score.oracle_turn(ans, turn["expect"], m); self.assertTrue(o["correct"], [i for i in o["items"] if not i["ok"]])
        finally:
            client.close()

if __name__ == "__main__":
    unittest.main()
