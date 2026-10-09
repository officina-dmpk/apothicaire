"""Tests of the decision harness (decision/harness.py, decision/run_harness.py; D-01 step 4).

* the French templates on fixed engine results (golden strings), through the digests of apothicaire.py, with a fake MCP client that
  answers synthetic engine JSON;
* the action mapping of every turn kind (which MCP calls, with which arguments) and the refusal / question paths (unknown route,
  missing dose unit, missing infusion duration, a duration in another time unit, a parameter not computed for the route, a fit that
  is not wired, an answer outside the options);
* the state: built exactly as decision/make_dataset.py builds it (compared with the scripted rows of the 25 benchmark exercises);
* end to end against the real caladrius-mcp (skipped when it is not built): one turn, then one whole exercise through
  run_harness.run_exercise with gold decisions, judged by the oracle of bench/score.py.
Synthetic numbers only.
"""
import copy, json, os, re, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
sys.path.insert(0, AGENT); sys.path.insert(0, os.path.join(AGENT, "decision"))
import apothicaire, gate  # noqa: E402
import harness as H  # noqa: E402
import make_dataset as md  # noqa: E402
import run_harness as rh  # noqa: E402
from bench import make_exercises as mk, scripts, score  # noqa: E402

# ---------------------------------------------------------------- a fake engine (synthetic values, engine JSON shapes)
UNIT_WARNING = {"code": "missing_unit", "message": "the dose has no unit; derived units (AUC, clearance, volume) cannot be named"}
WORKSHEET = {"worksheet": {"id": 1, "name": "donnees", "rows": 6, "subjects": ["1"],
                           "columns": [{"name": "time", "role": "time", "unit": "h"}, {"name": "conc", "role": "concentration", "unit": "mg/L"}],
                           "derived_units": {"auc": "h*mg/L", "aumc": "h^2*mg/L", "half_life": "h", "lambda_z": "1/h", "mrt": "h"},
                           "unit_warnings": [UNIT_WARNING]}}
VALUES = {"linear": {"cmax": 812.5, "tmax": 1.5, "auclast": 4012.25, "aucinf.obs": 4210.5, "aucpext.obs": 4.7083, "lambda.z": 0.1155,
                     "lambda.z.n.points": 4.0, "adj.r.squared": 0.9981, "half.life": 6.0012, "cl.obs": 0.0475, "vz.obs": 0.4113,
                     "mrt.obs": 7.25, "mrt.iv.obs": 6.75, "tlag": 0.0},
          "lin_up_log_down": {"cmax": 812.5, "tmax": 1.5, "auclast": 3950.75, "aucinf.obs": 4149.0, "aucpext.obs": 4.7843, "lambda.z": 0.1155,
                              "lambda.z.n.points": 4.0, "adj.r.squared": 0.9981, "half.life": 6.0012, "cl.obs": 0.0482, "vz.obs": 0.4174,
                              "mrt.obs": 7.31, "mrt.iv.obs": 6.81, "tlag": 0.0}}
REASON = "not defined for this route of administration"

class FakeMCP:
    """Answers data_import / nca_run / analysis_get / analysis_compare with synthetic engine JSON; records every call."""
    def __init__(self):
        self.tools = {n: {} for n in ("data_import", "nca_run", "analysis_get", "analysis_compare")}
        self.calls, self.analyses = [], {}

    def call(self, name, args):
        self.calls.append((name, copy.deepcopy(args)))
        if name == "data_import": return True, json.dumps(WORKSHEET)
        if name == "nca_run":
            aid, m = 2 + len(self.analyses), (args.get("options") or {}).get("auc_method", "linear")
            params = [{"name": "c0", "value": {"not_calculated": "not_applicable_to_route"}}] + \
                     [{"name": k, "value": {"value": v}} for k, v in VALUES[m].items()]
            subject = {"subject": "1", "dose": float(args["dose"]), "route": args["route"], "flag_messages": [],
                       "not_calculated_messages": {"c0": REASON}, "outcome": {"ok": {"parameters": params, "flags": []}}}
            self.analyses[aid] = {"id": aid, "kind": "nca", "label": "NCA of donnees, all subjects", "status": {"state": "fresh"},
                                  "spec": {"worksheet": args["worksheet"], "dose": float(args["dose"]), "route": args["route"],
                                           "options": {"auc_method": m}},
                                  "result": {"kind": "nca", "subjects": [subject]}}
            return True, json.dumps(self.analyses[aid])
        if name == "analysis_get":
            if args["analysis"] not in self.analyses: return False, f"unknown_analysis: there is no analysis {args['analysis']}"
            return True, json.dumps(self.analyses[args["analysis"]])
        if name == "analysis_compare":
            info = lambda i: {"analysis": i, "kind": "nca", "label": "NCA of donnees, all subjects", "status": "fresh", "subject": "1"}
            row = {"parameter": "auclast", "a": 4012.25, "b": 3950.75, "difference": -61.5, "difference_unit": None,
                   "relative_percent": -1.5328, "ratio": 0.984672, "unit_a": None, "unit_b": None, "not_comparable": None}
            return True, json.dumps({"a": info(args["a"]), "b": info(args["b"]), "rows": [row]})
        return False, f"unknown tool {name}"

    def close(self): pass

def message(route="par voie orale", dose="400 mg"):
    return (f"Voici les données d'un exercice ({dose} {route} ; temps en h, concentration en mg/L) :\n"
            "time (h),conc (mg/L)\n0,0\n0.5,310.2\n1.5,812.5\n4,520.1\n8,250.3\n12,120.7\n"
            "Fais l'analyse non compartimentale avec la méthode linéaire des trapèzes et donne-moi les paramètres.")

BASE = {"analysis": "none_needed", "route": "oral", "auc_method": "not_applicable", "parameter_asked": "none", "dose_has_unit": "true",
        "is_not_available": "false", "compare_pair": "not_applicable"}
NCA = dict(BASE, analysis="nca", auc_method="linear", parameter_asked="several")

class Scripted:
    """A decision model that answers a fixed sequence of answer sets and records the states it was shown."""
    def __init__(self, *answers): self.answers, self.states = list(answers), []
    def __call__(self, state, questions):
        self.states.append((state, questions)); return self.answers.pop(0)

def run(*turns, msg=None):
    """Runs (answers per decide call, ...) turns: each item is (user text or None for the first message, [answer sets])."""
    answers = [a for _, aa in turns for a in aa]
    dec = Scripted(*answers); h = H.Harness(dec, mcp=FakeMCP()); out = []
    for text, _ in turns: out.append(h.turn(text or msg or message()))
    return h, out, dec

HEADER = "Résultats de Caladrius (analyse 2, méthode d'AUC trapèzes linéaires (linear), dose 400, voie orale (extravasculaire)) :"
WARN = "Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named »."
TABLE = "\n".join([HEADER, "- Cmax : 812.5 mg/L", "- Tmax : 1.5 h", "- AUC(0-tlast) : 4012.25 h*mg/L", "- AUC(0-inf) : 4210.5 h*mg/L",
                   "- AUC extrapolée (%) : 4.7083 %", "- λz (constante d'élimination terminale) : 0.1155 1/h",
                   "- Nombre de points de la régression terminale : 4", "- R² ajusté de la régression terminale : 0.9981",
                   "- t½ (demi-vie terminale) : 6.0012 h", "- CL/F (clairance) : 0.0475 dose unit/(h*mg/L)",
                   "- Vz/F (volume de distribution) : 0.4113 dose unit/(mg/L)", "- MRT (temps moyen de résidence) : 7.25 h",
                   "C0 (concentration initiale extrapolée) n'est pas calculé par Caladrius (« not defined for this route of administration »).", WARN])
RECALL = "\n".join(["Réglages de l'analyse 2 tels que Caladrius les a enregistrés :",
                    "- Dose : 400 mg (unité de votre premier message ; Caladrius a reçu la dose sans unité)",
                    "- Voie d'administration : voie orale (extravasculaire)", "- Méthode d'AUC : trapèzes linéaires (linear)"])
COMPARE = "\n".join(["Comparaison calculée par Caladrius entre l'analyse 2 et l'analyse 3 (b - a) :",
                     "- AUC(0-tlast), méthode linéaire (analyse 2) : 4012.25 h*mg/L",
                     "- AUC(0-tlast), méthode linear-up/log-down (analyse 3) : 3950.75 h*mg/L",
                     "- Différence (b - a) : -61.5 h*mg/L", "- Différence relative : -1.5328 %", "- Rapport b/a : 0.984672"])
REFUSAL_C0 = ("C0 (concentration initiale extrapolée) n'est pas calculé par Caladrius pour cette voie d'administration : voie orale "
              "(extravasculaire). Raison donnée par Caladrius : « not defined for this route of administration ».")

class TestTemplates(unittest.TestCase):
    """Golden strings: what the harness writes for fixed engine results."""
    def test_nca_table(self):
        h, out, _ = run((None, [NCA]))
        self.assertEqual(out[0][0], TABLE)

    def test_single_parameter(self):
        h, out, _ = run((None, [NCA]), ("Et la clairance ?", [dict(BASE, parameter_asked="cl")]))
        self.assertEqual(out[1][0], "\n".join([HEADER, "- CL/F (clairance) : 0.0475 dose unit/(h*mg/L)", WARN]))

    def test_recall(self):
        h, out, _ = run((None, [NCA]), ("Rappelle-moi la dose.", [BASE]))
        self.assertEqual(out[1][0], RECALL)

    def test_compare(self):
        cmp_ = dict(BASE, analysis="compare", auc_method="lin_up_log_down", parameter_asked="auclast", compare_pair="2+3")
        h, out, _ = run((None, [NCA]), ("Compare avec lin-up/log-down.", [cmp_, cmp_]))
        self.assertEqual(out[1][0], COMPARE)

    def test_refusal(self):
        h, out, _ = run((None, [NCA]), ("Quelle est C0 ?", [dict(BASE, is_not_available="true", parameter_asked="c0")]))
        self.assertEqual(out[1][0], REFUSAL_C0)
        self.assertRegex(out[1][0], scripts.NOT_AVAILABLE)

    def test_value_text_drops_only_a_float_trailing_zero(self):
        self.assertEqual(H.value_text("1701680.0 min*ng/mL"), "1701680 min*ng/mL")
        self.assertEqual(H.value_text(4.0), "4")
        self.assertEqual(H.value_text(0.996288), "0.996288")
        self.assertEqual(H.value_text("10.05 h^2*mg/L"), "10.05 h^2*mg/L")
        self.assertEqual(H.value_text("3.0e-05 1/h"), "3.0e-05 1/h")
        self.assertEqual(H.value_text("-41195.6 min*ng/mL"), "-41195.6 min*ng/mL")

    def test_answers_hold_only_engine_numbers(self):
        """The gate finds no number outside the tool results and the user's messages in any template above."""
        cmp_ = dict(BASE, analysis="compare", auc_method="lin_up_log_down", parameter_asked="auclast", compare_pair="2+3")
        h, out, _ = run((None, [NCA]), ("cl", [dict(BASE, parameter_asked="cl")]), ("recall", [BASE]), ("cmp", [cmp_, cmp_]),
                        ("c0", [dict(BASE, is_not_available="true", parameter_asked="c0")]))
        allowed = gate.allowed_numbers([c["shown"] for c in h.tool_log], h.user_texts)
        for ans, _ in out:
            g = gate.check(ans, allowed=allowed)
            self.assertEqual(g["numbers_unverified"], 0, (ans, g["findings"]))

class TestActions(unittest.TestCase):
    """Which MCP calls each kind of turn makes."""
    def test_import_and_nca_once(self):
        h, out, _ = run((None, [NCA]), ("Cmax ?", [dict(BASE, parameter_asked="several")]))
        csv = "time (h),conc (mg/L)\n0,0\n0.5,310.2\n1.5,812.5\n4,520.1\n8,250.3\n12,120.7"
        self.assertEqual(h.mcp.calls, [
            ("data_import", {"name": "donnees", "csv": csv, "columns": [{"name": "time", "unit": "h"}, {"name": "conc", "unit": "mg/L"}]}),
            ("nca_run", {"worksheet": 1, "dose": 400, "route": "extravascular", "options": {"auc_method": "linear"}}),
            ("analysis_get", {"analysis": 2})])
        self.assertEqual(out[1][0], TABLE)

    def test_routes(self):
        for phrase, route, want in (("en bolus intraveineux", "iv_bolus", "iv_bolus"),
                                    ("en perfusion intraveineuse de 2 h", "iv_infusion", {"iv_infusion": {"duration": 2}}),
                                    ("en perfusion IV de 0,5 h", "iv_infusion", {"iv_infusion": {"duration": 0.5}})):
            h, _, _ = run((None, [dict(NCA, route=route)]), msg=message(phrase))
            self.assertEqual(h.mcp.calls[1], ("nca_run", {"worksheet": 1, "dose": 400, "route": want, "options": {"auc_method": "linear"}}))

    def test_auc_method_not_applicable_leaves_the_engine_default(self):
        h, _, _ = run((None, [dict(NCA, auc_method="not_applicable")]))
        self.assertEqual(h.mcp.calls[1], ("nca_run", {"worksheet": 1, "dose": 400, "route": "extravascular"}))

    def test_compare_reruns_then_decides_again(self):
        cmp_ = dict(BASE, analysis="compare", auc_method="lin_up_log_down", parameter_asked="auclast", compare_pair="2+3")
        h, out, dec = run((None, [NCA]), ("Compare.", [cmp_, cmp_]))
        self.assertEqual(h.mcp.calls[2:], [("nca_run", {"worksheet": 1, "dose": 400, "route": "extravascular", "options": {"auc_method": "lin_up_log_down"}}),
                                           ("analysis_compare", {"a": 2, "b": 3, "parameters": ["auclast"]})])
        info = out[1][1]
        self.assertEqual([d["outside_options"] for d in info["decisions"]], [["compare_pair"], []])   # "2+3" is offered only after the re-run
        self.assertEqual([[a["id"] for a in s["analyses"]] for s, _ in dec.states[1:]], [[2], [2, 3]])
        self.assertIn("2+3", dec.states[2][1]["compare_pair"]["criteria"])

    def test_compare_without_a_pair_asks(self):
        cmp_ = dict(BASE, analysis="compare")
        h, out, _ = run((None, [NCA]), ("Compare.", [cmp_]))
        self.assertEqual(out[1][0], "Quelles analyses faut-il comparer ? Analyses du projet : analyse 2 (NCA, linéaire).")
        self.assertEqual([c[0] for c in h.mcp.calls], ["data_import", "nca_run"])

    def test_reading_uses_the_analysis_of_the_decided_method(self):
        cmp_ = dict(BASE, analysis="compare", auc_method="lin_up_log_down", parameter_asked="auclast", compare_pair="2+3")
        h, out, _ = run((None, [NCA]), ("cmp", [cmp_, cmp_]), ("AUC lud ?", [dict(BASE, auc_method="lin_up_log_down", parameter_asked="auclast")]),
                        ("AUC ?", [dict(BASE, parameter_asked="auclast")]))
        self.assertEqual(h.mcp.calls[-2:], [("analysis_get", {"analysis": 3}), ("analysis_get", {"analysis": 2})])
        self.assertIn("- AUC(0-tlast) : 3950.75 h*mg/L", out[2][0]); self.assertIn("- AUC(0-tlast) : 4012.25 h*mg/L", out[3][0])

class TestRefusals(unittest.TestCase):
    """Nothing is run, nothing is guessed: the template says what is missing."""
    def no_engine_call(self, answers, msg=None):
        h, out, _ = run((None, [answers]), msg=msg)
        self.assertEqual(h.mcp.calls, [])
        self.assertIsNone(re.search(r"(?<![A-Za-z])\d", out[0][0]), out[0][0])     # no number (the 0 of "C0" is a name)
        return out[0][0]

    def test_unknown_route(self):
        self.assertEqual(self.no_engine_call(dict(NCA, route="unknown")), H.T_ASK_ROUTE)

    def test_dose_without_unit(self):
        self.assertEqual(self.no_engine_call(dict(NCA, dose_has_unit="false"), msg=message(dose="400")), H.T_ASK_DOSE_UNIT)

    def test_dose_not_found(self):
        self.assertEqual(self.no_engine_call(NCA, msg=message(dose="une dose")), H.T_ASK_DOSE)

    def test_infusion_without_duration(self):
        out = self.no_engine_call(dict(NCA, route="iv_infusion"), msg=message("en perfusion intraveineuse"))
        self.assertEqual(out, H.T_ASK_DURATION.format(t="h"))

    def test_infusion_duration_in_another_unit(self):
        out = self.no_engine_call(dict(NCA, route="iv_infusion"), msg=message("en perfusion intraveineuse de 30 min"))
        self.assertEqual(out, H.T_ASK_DURATION_UNIT.format(u="min", t="h"))

    def test_fit_not_wired(self):
        self.assertEqual(self.no_engine_call(dict(NCA, analysis="fit_pk1")),
                         H.T_NOT_WIRED.format(what="ajustement d'un modèle à un compartiment"))

    def test_answer_outside_the_options(self):
        self.assertEqual(self.no_engine_call(dict(NCA, analysis="dance")), H.T_UNDECIDED.format(qs="type d'analyse"))

    def test_no_data(self):
        h = H.Harness(Scripted(), mcp=FakeMCP())
        self.assertEqual(h.turn("Bonjour, peux-tu m'aider ?")[0], H.T_NO_DATA)

    def test_reading_before_any_analysis(self):
        self.assertEqual(self.no_engine_call(dict(BASE, parameter_asked="cmax")), H.T_NO_ANALYSIS)

    def test_refusal_before_any_analysis(self):
        out = self.no_engine_call(dict(BASE, is_not_available="true", parameter_asked="c0"))
        self.assertEqual(out, "C0 (concentration initiale extrapolée) n'est pas calculé par Caladrius pour cette voie d'administration ; "
                              "aucune analyse n'est encore faite.")

    def test_refusal_overruled_when_the_engine_computed_the_parameter(self):
        h, out, _ = run((None, [NCA]), ("Tlag ?", [dict(BASE, is_not_available="true", parameter_asked="tlag")]))
        self.assertEqual(out[1][0], "\n".join([HEADER, "- Tlag (temps de latence) : 0 h", WARN]))
        self.assertEqual(out[1][1]["notes"], ["is_not_available overruled: Caladrius computed tlag"])

    def test_engine_error_is_quoted_not_hidden(self):
        h = H.Harness(Scripted(NCA, dict(BASE, parameter_asked="cmax")), mcp=FakeMCP())
        h.turn(message()); h.analyses[0]["id"] = 9                       # a stale id: the engine refuses it
        ans = h.turn("Cmax ?")[0]
        self.assertEqual(ans, "Caladrius a refusé l'appel analysis_get : « unknown_analysis: there is no analysis 9 ». Je ne donne aucune valeur.")

    def test_normalize_answers(self):
        qs = md.questions_for([2])
        got, outside = H.normalize_answers({"analysis": {"label": "nca"}, "dose_has_unit": True, "route": "boat"}, qs)
        self.assertEqual((got["analysis"], got["dose_has_unit"], got["route"]), ("nca", "true", None))
        self.assertEqual(sorted(outside), ["auc_method", "compare_pair", "is_not_available", "parameter_asked", "route"])

class TestState(unittest.TestCase):
    """The harness's state is the dataset's state: compared with the scripted-wording rows of the 25 benchmark exercises."""
    def test_states_match_the_dataset(self):
        n = 0
        for d in mk.list_exercises():
            meta, csv = mk.load(d)
            rows = [r for r in md.exercise_rows(meta, csv, True) if json.loads(r["factors"])["scripted_wording"]]
            gold = {rh.state_key(json.loads(r["state"])): (json.loads(r["state"]), {q: g["label"] for q, g in json.loads(r["gold"]).items()})
                    for r in rows}
            seen = []
            def decide(state, questions):
                ref, answers = gold[rh.state_key(state)]
                seen.append((state, ref, questions)); return answers
            h = H.Harness(decide, mcp=FakeMCP())
            for t in scripts.build_script(meta, csv): h.turn(t["question"])
            self.assertEqual(len({rh.state_key(s) for s, _, _ in seen}), 8, meta["id"])
            for state, ref, questions in seen:
                if state["analyses"] == ref["analyses"]:
                    self.assertEqual(state, ref); self.assertEqual(questions, md.questions_for([a["id"] for a in ref["analyses"]])); n += 1
                else:                                                    # a "late" row, or the compare turn before its re-run
                    self.assertEqual({**state, "analyses": None}, {**ref, "analyses": None})
        self.assertGreater(n, 100)

    def test_split_first_message(self):
        meta, csv = mk.load(mk.list_exercises()[0])
        t1 = scripts.build_script(meta, csv)[0]["question"]
        parts = md.split_first_message(t1)
        self.assertEqual(parts["csv"], csv.strip())
        self.assertEqual(parts["intro"], t1.split("\n")[0]); self.assertEqual(parts["request"], t1.split("\n")[-1])
        self.assertEqual(md.split_first_message("Bonjour\nrien\nFais une NCA.")["csv"], "")

@unittest.skipUnless(os.path.exists(apothicaire.MCP_BIN), "caladrius-mcp is not built (see apothicaire.MCP_BIN)")
class TestRealEngine(unittest.TestCase):
    def test_first_turn(self):
        meta, csv = mk.load(os.path.join(mk.OUT, "ex05_iv_infusion"))
        st = scripts.build_script(meta, csv)[0]
        h = H.Harness(lambda s, q: dict(NCA, route="iv_infusion"))
        try: ans, _ = h.turn(st["question"])
        finally: h.close()
        o = score.oracle_turn(ans, st["expect"], meta)
        self.assertTrue(o["correct"], (ans, o))
        allowed = gate.allowed_numbers([c["shown"] for c in h.tool_log], h.user_texts)
        self.assertEqual(gate.check(ans, allowed=allowed)["numbers_unverified"], 0)
        self.assertEqual([c["name"] for c in h.tool_log], ["data_import", "nca_run"])
        self.assertEqual(h.tool_log[1]["args"], meta["ground_truth"]["nca"]["linear"]["nca_run_arguments"] | {"worksheet": 1})

    def test_whole_exercise_with_gold_decisions(self):
        """ex18: AUC values above a million (the trailing '.0' of the 6-digit digest must not reach the answer)."""
        meta, csv = mk.load(os.path.join(mk.OUT, "ex18_pk2_iv_bolus"))
        index = {rh.state_key(json.loads(r["state"])): {q: g["label"] for q, g in json.loads(r["gold"]).items()}
                 for r in md.exercise_rows(meta, csv, True) if json.loads(r["factors"])["scripted_wording"]}
        decide = lambda state, questions: index[rh.state_key(state)]
        with tempfile.TemporaryDirectory() as tmp:
            rec = rh.run_exercise(os.path.join(mk.OUT, meta["id"]), tmp, decide)
        turns = rec["turns"]
        self.assertEqual([t.get("error") for t in turns], [None] * 8)
        self.assertTrue(all(t["oracle"]["correct"] for t in turns if t.get("oracle")), [t["answer"] for t in turns])
        self.assertTrue(all(t["score"]["correct"] for t in turns))
        self.assertEqual(sum(t["numbers_unverified_after"] for t in turns), 0)
        self.assertEqual(rec["tool_arg_audit"]["deviating_calls"], 0)
        self.assertTrue(turns[6]["compare_tool"]["usable"])

if __name__ == "__main__":
    unittest.main()
