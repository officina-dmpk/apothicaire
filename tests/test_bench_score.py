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

    def test_forbidden_value_copied_from_a_tool_result_is_not_counted(self):
        """2026-10-10: the decision harness prints Caladrius's own conversion ("soit 5.02147 L/h") next to the "dose unit" value; the
        "CL x 10^3" rule must not fire on a number the engine returned in that turn, and still fires on one the answer computed."""
        e = {"must": [{"label": "CL/F", "value": 0.00502147}], "must_not": [{"label": "CL/F x 10^3", "value": 5.02147}]}
        ans = "CL/F : 0.00502147 dose unit/(h*ng/mL), soit 5.02147 L/h (conversion faite par Caladrius avec la dose en mg)"
        units_session = json.dumps({"parameters": {"cl.obs": "5.02147 L/h"}})
        s = score.score_turn(ans, e, 0, [tool_result(**{"cl.obs": "0.00502147 dose unit/(h*ng/mL)"}), units_session])
        self.assertTrue(s["correct"]); self.assertEqual(s["forbidden"], []); self.assertEqual(s["forbidden_from_tools"], ["CL/F x 10^3"])
        s = score.score_turn(ans, e, 0)                                                        # no tool result given: counted, as before
        self.assertFalse(s["correct"]); self.assertEqual(s["forbidden"], ["CL/F x 10^3"]); self.assertEqual(s["forbidden_from_tools"], [])
        s = score.score_turn(ans.replace("5.02147", "5.021"), e, 0, [units_session])           # rounded by the answer: not verbatim
        self.assertEqual(s["forbidden"], ["CL/F x 10^3"])
        s = score.score_turn(ans + " ; donc 5021,47 mL/h", {"must_not": [{"label": "x", "value": 5021.47}]}, 0, [units_session])
        self.assertEqual(s["forbidden"], ["x"])                                                # converted by the answer itself
        s = score.score_turn(ans + " ou 5,021 L/h", e, 0, [units_session])                    # one copied hit, one computed hit
        self.assertEqual(s["forbidden"], ["CL/F x 10^3"])

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

    def cls(self, answer, kind=None, users=(), with_answer=False):
        f, allowed = findings_of(answer, self.tool, users)
        self.assertEqual(len(f), 1, (answer, f))
        return score.classify(f[0], allowed, kind, answer if with_answer else None)

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

    def test_local_arithmetic_uses_the_numbers_written_in_the_answer(self):
        # 3 digits: the percentage 3.5 % of 96.5 -> 100.0 is the model's own computation from numbers it wrote next to it
        ans = "AUC 100.0 contre 96.5 : écart 3,50 soit 3,63 %"
        f, allowed = findings_of(ans, self.tool)
        out = {x["text"]: score.classify(x, allowed, None, ans) for x in f}
        self.assertEqual(out["3,63 %"], "arithmetic")                       # (100.0 - 96.5) / 96.5 * 100
        self.assertEqual(out["3,50"], "arithmetic")                         # 100.0 - 96.5
        self.assertNotEqual(score.classify(f[0], allowed, None), "arithmetic")   # without the answer, 3 digits: not claimed

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


class TestRescoreWithToolResults(unittest.TestCase):
    """bench/run_bench.rescore passes each stored turn's tool results to score_turn: the turn's `tool_calls` and, for a decision-harness
    run, the units session's results (`unit_calls`) of that turn and the earlier ones (the harness caches the conversion of turn 1 and
    shows it again on the clearance turn)."""
    def test_rescore_skips_a_must_not_value_returned_by_the_units_session(self):
        import tempfile
        from bench import make_exercises as mk, run_bench as rb, scripts
        meta, csv = mk.load(os.path.join(mk.OUT, "ex02_oral_1"))                       # 400 mg against ng/mL
        script = scripts.build_script(meta, csv)
        cl, vz = scripts.truth_value(meta, "cl.obs"), scripts.truth_value(meta, "vz.obs")
        conv = lambda x: f"{x * 1000:.6g}"                                             # what Caladrius returns with the units (L/h, L)
        line = lambda st: chr(10).join(f"- {m['label']} : {m['value']:.6g}" for m in st["expect"].get("must", []))
        answers = {"import_nca": line(script[0]) + f"{chr(10)}CL/F soit {conv(cl)} L/h ; Vz/F soit {conv(vz)} L",
                   "clearance_volume": line(script[2]) + f"{chr(10)}soit {conv(cl)} L/h et {conv(vz)} L"}
        units_result = json.dumps({"parameters": {"cl.obs": f"{conv(cl)} L/h", "vz.obs": f"{conv(vz)} L"}})
        def record(with_shown):
            turns = []
            for k, st in enumerate(script):
                t = {"exercise": meta["id"], "turn": k + 1, "kind": st["kind"], "answer": answers.get(st["kind"], "pas calculé"),
                     "tool_calls": [], "numbers_unverified_after": 0, "score": {"correct": None}}
                if k == 0: t["unit_calls"] = [{"name": "nca_run", "ok": True, **({"shown": units_result} if with_shown else {})}]
                turns.append(t)
            return {"id": meta["id"], "turns": turns}
        with tempfile.TemporaryDirectory() as tmp:
            for with_shown in (True, False):
                with open(os.path.join(tmp, meta["id"] + ".json"), "w", encoding="utf-8") as f: json.dump(record(with_shown), f)
                rb.rescore(tmp, [meta["id"]])
                with open(os.path.join(tmp, meta["id"] + ".json"), encoding="utf-8") as f: turns = json.load(f)["turns"]
                for k in (0, 2):
                    sc = turns[k]["score"]
                    self.assertEqual(sc["missing"], [], turns[k]["kind"])
                    if with_shown: self.assertEqual((sc["forbidden"], sorted(sc["forbidden_from_tools"])), ([], ["CL/F x 10^3", "Vz/F x 10^3"]))
                    else: self.assertEqual(sorted(sc["forbidden"]), ["CL/F x 10^3", "Vz/F x 10^3"])

class TestRubric(unittest.TestCase):
    """The rubric of the frozen sets (FROZEN_SET.md §6.2, §7; score.rubric_turn), on the gold of the development set."""
    @classmethod
    def setUpClass(cls):
        from bench import make_exercises as mk, scripts
        cls.mk, cls.sc = mk, scripts
        cls.ex = {os.path.basename(d): mk.load(d) for d in mk.list_exercises()}

    def turn(self, ex, k):
        meta, csv = self.ex[ex]
        return self.sc.build_script(meta, csv)[k], meta

    def test_mutation_suite_on_the_development_set(self):
        """§7 pass criterion: every canonical answer and variant CORRECT, every mutation WRONG, on all 25 exercises."""
        from bench import mutations
        r = mutations.run([os.path.join(self.mk.OUT, i) for i in sorted(self.ex)], verbose=False)
        self.assertEqual(r["failures"], [])
        self.assertEqual(r["canonical"][0], r["canonical"][1]); self.assertEqual(r["mutations"][0], r["mutations"][1])
        self.assertGreater(r["mutations"][1], 1000)

    def test_the_seven_probes_of_the_triage(self):
        """RT-B3 (red-team triage of 2026-10-19): the seven answers the development scorer accepted are WRONG."""
        t4, meta = self.turn("ex13_oral_1", 3)
        p = meta["ground_truth"]["nca"]["linear"]["parameters"]
        vals = [v["value"] for v in p.values() if isinstance(v, dict) and isinstance(v.get("value"), (int, float))]
        dump = "Tous les paramètres : " + " ; ".join(f"{x:.6g}".replace(".", ",") for x in vals) + ". Oui, acceptable."
        probes = [(t4, meta, dump), (t4, meta, "Les résultats sont 3,30899 h et 9,81301 % ; non, pas acceptable.")]
        for ex in ("ex01_iv_bolus", "ex02_oral_1"):
            t2, m = self.turn(ex, 1)
            pp = m["ground_truth"]["nca"]["linear"]["parameters"]; cm, tm = pp["cmax"], pp["tmax"]
            c, t = f"{cm['value']:g} {cm['unit']}", f"{tm['value']:g} {tm['unit']}"
            extra = f", C0 = {pp['c0']['value']:g} {pp['c0']['unit']}" if ex == "ex01_iv_bolus" else ""
            probes += [(t2, m, f"Cmax = -{c}, Tmax = -{t}{extra}"), (t2, m, f"Cmax is NOT {c}, Tmax is NOT {t}{extra}")]
            if ex == "ex01_iv_bolus":
                probes.append((t2, m, f"Cmax = 999 {cm['unit']} ; l'ancienne Cmax, fausse, était {c}. Tmax = {t}{extra}"))
        self.assertEqual(len(probes), 7)
        for turn, m, a in probes:
            r = score.rubric_turn(a, turn, m)
            self.assertFalse(r["correct"], a); self.assertTrue(r["reasons"], a)

    def test_rules_one_by_one(self):
        t2, meta = self.turn("ex01_iv_bolus", 1)                      # C0, Cmax = 3.679 mg/L, Tmax = 2.7 h
        pp = meta["ground_truth"]["nca"]["linear"]["parameters"]
        c0 = f"{pp['c0']['value']:.6g}"
        ok = f"C0 = {c0} mg/L, Cmax = 3,679 mg/L et Tmax = 2,7 h."
        self.assertTrue(score.rubric_turn(ok, t2, meta)["correct"])
        cases = {"unlabelled": f"{c0} mg/L, 3,679 mg/L, 2,7 h", "sign": ok.replace("3,679", "-3,679"),
                 "negation": ok.replace("Cmax = 3,679", "Cmax n'est pas 3,679"), "disowned": ok + " L'ancienne Cmax, fausse, était 4,12 mg/L ; Cmax = 4,12",
                 "contradiction": ok + " Autre lecture : Cmax = 4,12 mg/L.", "unit": ok.replace("3,679 mg/L", "3,679 ng/mL"),
                 "dump": ok + " Par ailleurs AUC(0-tlast) = 67,0394 h·mg/L, AUC(0-inf) = 68,8061 h·mg/L, t½ = 9,94762 h et MRT = 14,8167 h."}
        for name, a in cases.items():
            with self.subTest(name):
                self.assertFalse(score.rubric_turn(a, t2, meta)["correct"], a)
        # legitimate: an obs/pred pair, a threshold, a 3-digit rounding, a unit rewritten, the badge cut off
        for a in (ok + " (Cmax prédite : sans objet)", ok.replace("3,679 mg/L", "3,68 µg/mL"), ok + "\n\n⚠ 1 nombre non vérifié : 12"):
            with self.subTest(a=a): self.assertTrue(score.rubric_turn(a, t2, meta)["correct"], score.rubric_turn(a, t2, meta)["reasons"])

    def test_verdict(self):
        self.assertEqual(score.verdict_of("**Est-ce acceptable ?** Oui. Le seuil est de 20 %."), "acceptable")
        self.assertEqual(score.verdict_of("Est-ce acceptable ? Non : 25 % dépasse le seuil."), "not_acceptable")
        self.assertEqual(score.verdict_of("**Acceptabilité** : oui."), "acceptable")
        self.assertEqual(score.verdict_of("L'extrapolation n'est pas acceptable."), "not_acceptable")
        self.assertEqual(score.verdict_of("C'est inacceptable."), "not_acceptable")
        self.assertEqual(score.verdict_of("C'est acceptable, ou pas acceptable."), "both")
        self.assertIsNone(score.verdict_of("Le pourcentage extrapolé est 3 %."))
        t4, meta = self.turn("ex13_oral_1", 3)                       # 9.8 % extrapolated: acceptable
        base = "t½ = 3,30899 h ; le pourcentage d'AUC extrapolé est 9,81301 %."
        self.assertTrue(score.rubric_turn(base + " C'est acceptable.", t4, meta)["correct"])
        self.assertFalse(score.rubric_turn(base + " Ce n'est pas acceptable.", t4, meta)["correct"])
        self.assertFalse(score.rubric_turn(base, t4, meta)["correct"])
        band = json.loads(json.dumps(meta)); band["ground_truth"]["nca"]["linear"]["parameters"]["aucpext.obs"]["value"] = 19.5
        tb = self.sc.build_script(band, self.ex["ex13_oral_1"][1])[3]
        for v in ("C'est acceptable.", "Ce n'est pas acceptable."):            # 18-22 %: either verdict, if the value is stated
            self.assertTrue(score.rubric_turn("t½ = 3,30899 h ; % de l'AUC extrapolé : 19,5 %. " + v, tb, band)["correct"])

    def test_a_threshold_of_another_quantity_is_no_verdict(self):
        """Stored answers the rubric of 2026-10-21 read as "both verdicts": the R² or the span ratio above its threshold."""
        for a in ("**Verdict : acceptable.** L'extrapolation post-tlast (2,7 %) est bien en dessous du seuil de 20 %, et le R² ajusté de la "
                  "régression λz (0,9977) dépasse le seuil de 0,9.",                                       # ex07 seed 2, 27B + scope
                  "**Verdict : acceptable.** L'extrapolation de l'AUC (1,70 %) est bien en dessous du seuil de 20 %, et le ratio d'étendue "
                  "(span ratio = 4,57) dépasse le seuil minimal de 2,0.",                                  # ex22 seed 3, 27B + scope
                  "**Verdict : acceptable.** Le pourcentage extrapolé est nettement inférieur au seuil de 20 % utilisé par Caladrius. La "
                  "régression de λz est bonne (adj. R² de 0.999389, rapport d'étendue de 2.91, supérieur au seuil de 2).",   # ex01 seed 1, Sonnet + scope
                  "**Acceptable ?** Oui :\n- La durée couverte vaut 2,9 demi-vies, au-dessus du seuil de 2.",
                  "C'est acceptable. Le rapport d'étendue n'est que modérément au-dessus du seuil.",
                  "La valeur extrapolée est en dessous du seuil et le R² est au-dessus du seuil : c'est acceptable."):
            with self.subTest(a=a): self.assertEqual(score.verdict_of(a), "acceptable")
        # the threshold of the extrapolation still decides, whatever is written next to it
        for a in ("L'extrapolation (25 %) dépasse le seuil de 20 %, malgré un R² de 0,99.", "25 % dépasse le seuil.",
                  "L'AUC extrapolée, calculée sur 3 points, dépasse le seuil de 20 %.",
                  "L'extrapolation est au-dessus du seuil de 20 %. Le R² ajusté dépasse le seuil de 0,9.",
                  "Ce n'est pas acceptable, et le span ratio est sous le seuil de 2.", "The extrapolation exceeds 20 %; R² is above the threshold of 0.9."):
            with self.subTest(a=a): self.assertEqual(score.verdict_of(a), "not_acceptable")
        self.assertEqual(score.verdict_of("C'est acceptable. L'extrapolation est au-dessus du seuil de 20 %."), "both")
        self.assertEqual(score.verdict_of("L'AUMC extrapolée dépasse le seuil de 20 %, mais l'AUC extrapolée est sous le seuil de 20 %."), "acceptable")
        self.assertIsNone(score.verdict_of("Le span ratio est sous le seuil de 2."))                # a threshold of another quantity alone says nothing
        self.assertIsNone(score.verdict_of("Le R² ajusté dépasse le seuil de 0,9."))

    def test_method_labels_and_layouts_of_the_compare_turn(self):
        """Stored compare answers the rubric of 2026-10-21 failed: the lin-up/log-down AUC, right, was not read."""
        cases = {"ex08_oral_1": "**AUC(0-tlast) :**\n- Méthode linéaire : 46 762,6 min·ng/mL\n- Méthode linéaire-haut/log-avant-bas : 42 680,3 "
                                "min·ng/mL\n\n**Différence :**\n- Valeur absolue : **4 082,31 min·ng/mL**\n- Pourcentage : **8,73 %**",
                 "ex18_pk2_iv_bolus": "Avec la méthode **linear-up/log-down** (analyse #3, bolus IV, dose 200 mg) :\n\n- **AUC(0–tlast)** : 1 660 490 "
                                      "min·ng/mL\n\nComparaison avec la méthode linéaire (analyse #2, AUC(0–tlast) = 1 701 680 min·ng/mL) :\n\n"
                                      "- **Différence en valeur absolue** : −41 195,6 min·ng/mL (la méthode lin-up/log-down donne une AUC plus faible)\n"
                                      "- **Différence en pourcentage** : −2,42 %",
                 "ex04_oral_1_lag": "L'AUC(0–tlast) passe de **73 402,9 h·ng/mL** (méthode linéaire) à **68 899,9 h·ng/mL** (méthode linear-up/log-down)."
                                    "\n\n- **Différence en valeur absolue** : **4 503 h·ng/mL**\n- **Différence en pourcentage** : **6,13463 %**",
                 "ex15_oral_0": "L'AUC(0–tlast) passe de **92,0519 h·mg/L** (méthode linéaire) à **85,5868 h·mg/L** (méthode linear-up/log-down).\n\n"
                                "- **Différence en valeur absolue** : −6,46509 h·mg/L\n- **Différence en pourcentage** : −7,02331 %"}
        for ex, a in cases.items():
            with self.subTest(ex):
                t7, meta = self.turn(ex, 6)
                self.assertTrue(score.rubric_turn(a, t7, meta)["correct"], score.rubric_turn(a, t7, meta)["reasons"])
        t7, meta = self.turn("ex04_oral_1_lag", 6)
        stale = cases["ex04_oral_1_lag"].replace("68 899,9", "73 402,9")                            # the linear value under the other method
        swapped = cases["ex04_oral_1_lag"].replace("73 402,9", "@").replace("68 899,9", "73 402,9").replace("@", "68 899,9")
        for a in (stale, swapped):
            self.assertIn("AUC(0-tlast) lin-up/log-down: not stated with its label", score.rubric_turn(a, t7, meta)["reasons"])
        t7, meta = self.turn("ex18_pk2_iv_bolus", 6)
        self.assertFalse(score.rubric_turn(cases["ex18_pk2_iv_bolus"].replace("1 660 490", "1 701 680"), t7, meta)["correct"])     # stale, under a heading

    def test_difference_under_a_heading(self):
        t7, meta = self.turn("ex25_oral_1", 6)                       # seed 3, Sonnet + scope
        a = ("**AUC(0-tlast)**\n\n| Méthode | Valeur |\n|---|---|\n| Linéaire (analyse n°2) | 16951.2 h·ng/mL |\n| Linear-up/log-down (analyse n°3) | "
             "16012.2 h·ng/mL |\n\n**Différence (log-down moins linéaire) :**\n- Absolue : -939.022 h·ng/mL\n- Relative : -5.53956 %\n\nLa méthode "
             "linear-up/log-down donne donc une AUC(0-tlast) plus faible. Aucun flag qualité n'a été levé pour cette analyse.")
        self.assertTrue(score.rubric_turn(a, t7, meta)["correct"], score.rubric_turn(a, t7, meta)["reasons"])
        self.assertFalse(score.rubric_turn(a.replace("-939.022", "-1234.56"), t7, meta)["correct"])
        self.assertFalse(score.rubric_turn(a.replace("-5.53956", "-7.53956"), t7, meta)["correct"])

    def test_a_count_written_in_words(self):
        t5, meta = self.turn("ex06_oral_0", 4)                       # seed 1, 27B + scope: 3 points
        a = "Trois points ont servi à la régression de λz (aux temps 5,7 h, 8,8 h et 14 h), et le R² ajusté est de **0,999966**."
        self.assertTrue(score.rubric_turn(a, t5, meta)["correct"], score.rubric_turn(a, t5, meta)["reasons"])
        self.assertTrue(score.rubric_turn("Nombre de points : trois. R² ajusté = 0,999966.", t5, meta)["correct"])
        for w in ("Deux points ont servi à la régression", "Quatre points ont servi à la régression", "Ce ne sont pas trois points qui ont servi à la régression"):
            with self.subTest(w): self.assertFalse(score.rubric_turn(a.replace("Trois points ont servi à la régression", w), t5, meta)["correct"])
        self.assertEqual(score.rubric_turn("Sept points", self.turn("ex01_iv_bolus", 1)[0], meta)["reasons"][:1],
                         score.rubric_turn("", self.turn("ex01_iv_bolus", 1)[0], meta)["reasons"][:1])                # other turns do not read the word

    def test_compare_difference_and_percentage_are_required(self):
        t7, meta = self.turn("ex02_oral_1", 6)
        lin, lud = self.sc.truth_value(meta, "auclast"), self.sc.truth_value(meta, "auclast", "lin_up_log_down")
        d, p = lud - lin, (lud - lin) / lin * 100
        full = f"AUC(0-tlast) linear-up/log-down = {lud:.6g} h·ng/mL ; différence = {d:.6g} h·ng/mL ; soit {p:.6g} %."
        self.assertTrue(score.rubric_turn(full, t7, meta)["correct"], score.rubric_turn(full, t7, meta)["reasons"])
        self.assertTrue(score.rubric_turn(full.replace(f"{d:.6g}", f"{abs(d):.6g}").replace(f"{p:.6g}", f"{abs(p):.6g}"), t7, meta)["correct"])
        self.assertFalse(score.rubric_turn(f"AUC(0-tlast) linear-up/log-down = {lud:.6g} h·ng/mL.", t7, meta)["correct"])
        self.assertFalse(score.rubric_turn(full.replace(f"= {lud:.6g}", f"= {lin:.6g}"), t7, meta)["correct"])            # stale
        self.assertFalse(score.rubric_turn(full + f" Méthode linéaire : {lin * 1.1:.6g} h·ng/mL.", t7, meta)["correct"])   # optional but wrong
        self.assertTrue(score.rubric_turn(full + f" Méthode linéaire : {lin:.6g} h·ng/mL.", t7, meta)["correct"])

    def test_the_draw_of_the_human_labelling_holds_no_verdict(self):
        from bench import rubric_review as rr
        picks, _ = rr.draw()
        self.assertEqual(picks, rr.draw()[0])                        # seeded
        self.assertEqual(len({p["id"] for p in picks}), 40)
        kinds = [rr._stored_turn(p)[1]["kind"] for p in picks]
        self.assertEqual({k: kinds.count(k) for k in kinds}, {k: 5 for k in self.sc.KINDS})
        for p in picks: self.assertEqual(set(p), {"config", "folder", "seed", "exercise", "turn", "gold", "id"})

    def test_outcome_classes_in_order(self):
        rub = lambda ok: {"correct": ok, "items": [{"ok": ok}], "reasons": [] if ok else ["x"]}
        base = {"kind": "cmax_tmax", "answer": "Cmax = 1", "wall_s": 10, "rounds": 2}
        self.assertEqual(score.outcome_of({**base, "error": "LLMError"}, rub(True)), "ERROR")
        self.assertEqual(score.outcome_of({**base, "answer": ""}, rub(True)), "ERROR")
        self.assertEqual(score.outcome_of({**base, "wall_s": 301}, rub(True)), "TIMEOUT")
        self.assertEqual(score.outcome_of({**base, "rounds": 8}, rub(True)), "LOOP")
        self.assertEqual(score.outcome_of({**base, "tools_withdrawn": True}, rub(True)), "LOOP")
        self.assertEqual(score.outcome_of({**base, "answer": "(stopped: too many tool rounds)"}, rub(False)), "LOOP")
        self.assertEqual(score.outcome_of({**base, "answer": "Je ne peux pas répondre sans résultat."}, rub(False)), "ABSTAINED")
        self.assertEqual(score.outcome_of({**base, "kind": "not_available", "answer": "Impossible : non calculé."}, rub(True)), "CORRECT")
        self.assertEqual(score.outcome_of(base, rub(False)), "WRONG")
        self.assertEqual(score.outcome_of(base, rub(True)), "CORRECT")

if __name__ == "__main__":
    unittest.main()
