"""Tests of the out-of-distribution evaluation (decision/eval_ood.py).

* conversion of three synthetic request lines (an NCA request of turn 1, a compare request with prior analyses, a not-available request)
  into rows of the training format: the state and the questions are compared with the rows decision/make_dataset.py builds;
* rejection of malformed lines, with their reasons;
* the majority decider, the scoring (per question, per tag, calibration, wrong decisions) on fake deciders;
* end to end against the real caladrius-mcp (skipped when it is not built): the gold decisions through the harness.
No model, no GPU. Synthetic data only: the exercises are the benchmark's own.
"""
import json, os, random, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
sys.path.insert(0, AGENT); sys.path.insert(0, os.path.join(AGENT, "decision"))
import apothicaire  # noqa: E402
import eval_ood as E  # noqa: E402
import harness as H  # noqa: E402
import make_dataset as md  # noqa: E402
from bench import make_exercises as mk, scripts  # noqa: E402

EX = "ex02_oral_1"                                    # oral, 400 mg, h and ng/mL, 12 rows, no BLQ
META, CSV = mk.load(os.path.join(mk.OUT, EX))
SCRIPT = {t["kind"]: t for t in scripts.build_script(META, CSV)}

def gold(**kw):
    g = {"analysis": "none_needed", "route": "oral", "auc_method": "not_applicable", "dose_has_unit": True, "is_not_available": False,
         "compare_pair": "not_applicable", "asked": []}
    g.update(kw); return g

LINE_NCA = {"id": "ood-001", "exercise": EX, "turn": 1, "prior_analyses": [],
            "request": "J'ai donné 400 mg par voie orale, donne-moi la cmax et le tmax stp", "tags": ["colloquial", "typo"],
            "gold": gold(analysis="nca", auc_method="linear", asked=["cmax", "tmax"])}
LINE_COMPARE = {"id": "ood-002", "exercise": EX, "turn": 3, "prior_analyses": [{"id": 1, "auc_method": "linear"}, {"id": 2, "auc_method": "lin_up_log_down"}],
                "request": SCRIPT["compare"]["question"], "tags": ["compare-methods"],
                "gold": gold(analysis="compare", auc_method="lin_up_log_down", compare_pair="1+2", asked=["auclast"])}
LINE_NA = {"id": "ood-003", "exercise": EX, "turn": 2, "prior_analyses": [{"id": 1, "auc_method": "linear"}],
           "request": "C0 stp ?", "tags": ["not-available", "abbreviation"],
           "gold": gold(is_not_available=True, asked=["c0"])}
LINES = [LINE_NCA, LINE_COMPARE, LINE_NA]

def read(path):
    with open(path, encoding="utf-8") as f: return f.read()

def convert(*lines):
    return [E.convert_line(json.loads(json.dumps(l))) for l in lines]

def write_lines(path, objs):
    with open(path, "w", encoding="utf-8") as f:
        for o in objs: f.write((o if isinstance(o, str) else json.dumps(o, ensure_ascii=False)) + "\n")


class TestConversion(unittest.TestCase):
    def test_nca_request_of_turn_one(self):
        it = convert(LINE_NCA)[0]; row = it["row"]
        state, qs, g = json.loads(row["state"]), json.loads(row["questions"]), json.loads(row["gold"])
        self.assertEqual(row["id"], "ood-001"); self.assertEqual(row["split"], "ood"); self.assertEqual(row["n_questions"], 20)
        self.assertEqual(set(qs), set(md.questions_for([])))
        self.assertEqual(qs, md.questions_for([]))
        self.assertEqual(state["analyses"], [])
        self.assertEqual(state["user_dose_sentence"], LINE_NCA["request"]); self.assertEqual(state["request"], LINE_NCA["request"])
        self.assertEqual(state["data"], {"first_rows": CSV.strip().splitlines()[1:6], "header": "time (h),conc (ng/mL)",
                                         "n_rows": 12, "n_subjects": 1})
        self.assertEqual(state["notes"], [])
        self.assertEqual([k for k in g if k.startswith("asked_") and g[k]["label"] == "true"], ["asked_cmax", "asked_tmax"])
        self.assertEqual((g["analysis"]["label"], g["route"]["label"], g["auc_method"]["label"]), ("nca", "oral", "linear"))
        self.assertEqual((g["dose_has_unit"]["label"], g["is_not_available"]["label"], g["compare_pair"]["label"]), ("true", "false", "not_applicable"))
        self.assertEqual(g["asked_cmax"], md.gold_noul(True)); self.assertEqual(g["analysis"], md.gold_choice(md.ANALYSES, "nca"))
        self.assertEqual(set(g), set(qs))
        self.assertEqual(set(json.loads(row["label_agreement"])), set(qs))
        self.assertEqual(json.loads(row["factors"])["tags"], ["colloquial", "typo"])
        # what the harness will read of the message is the state of the row
        parts = md.split_first_message(it["message"])
        self.assertEqual((parts["intro"], parts["csv"], parts["request"]), (LINE_NCA["request"], CSV.strip(), LINE_NCA["request"]))

    def test_multi_line_first_message_and_blq_note(self):
        meta, csv = mk.load(os.path.join(mk.OUT, "ex07_iv_bolus"))                     # an exercise with a BLQ note
        self.assertTrue(meta.get("blq"))
        line = dict(LINE_NCA, exercise="ex07_iv_bolus", request="Dose : 20 mg en bolus IV\nsi tu peux\nDonne-moi C0.")
        it = convert(line)[0]; state = json.loads(it["row"]["state"])
        self.assertEqual(state["user_dose_sentence"], "Dose : 20 mg en bolus IV"); self.assertEqual(state["request"], "Donne-moi C0.")
        scripted = md.split_first_message(scripts.build_script(meta, csv)[0]["question"])["notes"]
        self.assertEqual(state["notes"], scripted + ["si tu peux"])

    def test_compare_request_equals_the_training_row(self):
        it = convert(LINE_COMPARE)[0]; row = it["row"]
        ref = md.build_row(META, CSV, True, "compare", 0, None, random.Random(0))
        self.assertEqual(json.loads(row["state"]), json.loads(ref["state"]))              # same state, analyses renumbered 2 and 3
        self.assertEqual(row["questions"], ref["questions"])
        self.assertEqual(row["gold"], ref["gold"])                                         # gold included: pair 1+2 became 2+3
        self.assertEqual(json.loads(row["state"])["analyses"], [{"id": 2, "kind": "nca", "auc_method": "linear"},
                                                                {"id": 3, "kind": "nca", "auc_method": "lin_up_log_down"}])
        self.assertEqual(json.loads(row["gold"])["compare_pair"]["label"], "2+3")
        self.assertTrue(any("renumbered" in w for w in it["warnings"]))

    def test_not_available_request(self):
        it = convert(LINE_NA)[0]; state, qs, g = (json.loads(it["row"][k]) for k in ("state", "questions", "gold"))
        first = md.split_first_message(SCRIPT["import_nca"]["question"])
        self.assertEqual(state["user_dose_sentence"], first["intro"]); self.assertEqual(state["request"], "C0 stp ?")
        self.assertEqual(state["analyses"], [{"id": 2, "kind": "nca", "auc_method": "linear"}])
        self.assertEqual(set(qs["compare_pair"]["criteria"]), {"not_applicable", "none_available"})   # one analysis: no pair
        self.assertEqual(g["is_not_available"]["label"], "true"); self.assertEqual(g["asked_c0"]["label"], "true")
        self.assertEqual(g["compare_pair"]["label"], "not_applicable")
        self.assertEqual(it["message"], "C0 stp ?")
        self.assertEqual(it["warnings"], ["prior analysis ids renumbered {\"1\": 2} (engine numbering)"])

    def test_ids_already_in_engine_numbering_are_not_renumbered(self):
        line = dict(LINE_COMPARE, prior_analyses=[{"id": 2, "auc_method": "linear"}, {"id": 3, "auc_method": "lin_up_log_down"}],
                    gold=gold(analysis="compare", auc_method="lin_up_log_down", compare_pair="2+3", asked=["auclast"]))
        it = convert(line)[0]
        self.assertEqual(it["warnings"], [])
        self.assertEqual(json.loads(it["row"]["gold"])["compare_pair"]["label"], "2+3")


class TestExerciseWithoutOracle(unittest.TestCase):
    """Exercises written blind (decision/ood/exercises/oodx*) have no ground_truth.nca: converting a request must not need it."""
    def test_first_message_is_the_one_of_the_script(self):
        self.assertEqual(scripts.first_message(META, CSV), scripts.build_script(META, CSV)[0]["question"])

    def test_line_on_an_exercise_without_nca_oracle_is_converted(self):
        meta = json.loads(json.dumps(META)); meta["ground_truth"] = {"data_import_columns": [], "oracle_note": "blind"}
        find = lambda ex: (meta, CSV, mk.OUT)
        with self.assertRaises(Exception): scripts.build_script(meta, CSV)       # the old path: KeyError 'nca'
        item = E.convert_line(json.loads(json.dumps(LINE_NCA)), find=find)
        ref = E.convert_line(json.loads(json.dumps(LINE_NCA)))
        self.assertEqual(item["row"]["state"], ref["row"]["state"])
        turn2 = json.loads(json.dumps(LINE_NA))
        self.assertEqual(E.convert_line(turn2, find=find)["row"]["state"], E.convert_line(json.loads(json.dumps(LINE_NA)))["row"]["state"])

    def test_nca_arguments_from_the_oracle_or_from_meta(self):
        self.assertEqual(E.nca_arguments(META), META["ground_truth"]["nca"]["linear"]["nca_run_arguments"] | {})
        for ex in sorted(os.listdir(mk.OUT)):                      # every benchmark exercise: meta.json and its oracle agree
            m, _ = mk.load(os.path.join(mk.OUT, ex)); ref = E.nca_arguments(m)
            blind = json.loads(json.dumps(m)); blind["ground_truth"] = {}
            got = E.nca_arguments(blind)
            self.assertEqual((got["dose"], got["route"]), (ref["dose"], ref["route"]), ex)
        root = os.path.join(E.OOD, "exercises")
        if os.path.isdir(root):
            for name in sorted(os.listdir(root)):
                m = E.find_exercise(name)[0]
                self.assertEqual(E.nca_arguments(m)["dose"], m["dose"]["amount"])

    def test_the_real_blind_exercises_are_all_found_and_scripted(self):
        root = os.path.join(E.OOD, "exercises")
        if not os.path.isdir(root): self.skipTest("no decision/ood/exercises")
        for name in sorted(os.listdir(root)):
            meta, csv, _ = E.find_exercise(name)
            first = E.scripted_first(meta, csv)
            self.assertTrue(first["intro"].startswith("Voici les donn") and first["csv"], name)


class TestRejection(unittest.TestCase):
    def reason(self, **changes):
        line = json.loads(json.dumps(LINE_NCA)); line.update(changes)
        with self.assertRaises(E.Reject) as cm: E.convert_line(line)
        return str(cm.exception)

    def test_reasons(self):
        line = json.loads(json.dumps(LINE_NCA)); del line["tags"]
        with self.assertRaises(E.Reject) as cm: E.convert_line(line)
        self.assertIn("missing field(s): tags", str(cm.exception))
        self.assertIn("unknown exercise", self.reason(exercise="nope_01"))
        self.assertIn("turn", self.reason(turn=0))
        self.assertIn("turn 1 cannot have prior analyses", self.reason(prior_analyses=[{"id": 1, "auc_method": "linear"}]))
        self.assertIn("unknown parameter key", self.reason(gold=gold(asked=["cmax", "bioavailability"])))
        self.assertIn("gold route", self.reason(gold=gold(route="rectal")))
        self.assertIn("boolean", self.reason(gold=gold(dose_has_unit="true")))
        two = [{"id": 1, "auc_method": "linear"}, {"id": 2, "auc_method": "lin_up_log_down"}]
        self.assertIn("outside the options", self.reason(turn=2, prior_analyses=two, gold=gold(compare_pair="none_available")))
        self.assertIn("auc_method", self.reason(turn=2, prior_analyses=[{"id": 1, "auc_method": "trapezoid"}]))
        self.assertIn("non-empty string", self.reason(request="  "))

    def test_pair_not_in_prior_analyses(self):
        r = self.reason(turn=2, prior_analyses=[{"id": 1, "auc_method": "linear"}, {"id": 2, "auc_method": "lin_up_log_down"}],
                        gold=gold(analysis="compare", compare_pair="1+5"))
        self.assertIn("not in prior_analyses", r)

    def test_directed_pair_keeps_the_users_order(self):
        """ood-015 / ood-072: "compare analysis 2 with analysis 1" is the pair 2+1, renumbered 3+2, not sorted into 2+3."""
        prior = [{"id": 1, "auc_method": "linear"}, {"id": 2, "auc_method": "lin_up_log_down"}]
        for pair, want in (("2+1", "3+2"), ("1+2", "2+3")):
            it = convert(dict(LINE_COMPARE, turn=2, prior_analyses=prior, request="Compare l'analyse 2 et l'analyse 1.",
                              gold=gold(analysis="compare", compare_pair=pair, asked=["auclast"])))[0]
            self.assertEqual(json.loads(it["row"]["gold"])["compare_pair"]["label"], want)
        self.assertEqual(E.translate_pair("2+1", {1: 2, 2: 3}, {"not_applicable": "", "2+3": "", "3+2": ""}), "3+2")
        self.assertEqual(E.translate_pair("3+2", {2: 2, 3: 3}, {"not_applicable": "", "2+3": "", "3+2": ""}), "3+2")

    def test_pair_that_is_not_a_key(self):
        r = self.reason(turn=2, prior_analyses=[{"id": 1, "auc_method": "linear"}], gold=gold(analysis="compare", compare_pair="none_available_x"))
        self.assertIn("neither a key", r)
        r = self.reason(turn=2, prior_analyses=[{"id": 1, "auc_method": "linear"}], gold=gold(analysis="compare", compare_pair="1+2"))
        self.assertIn("not in prior_analyses", r)

    def test_read_requests_collects_rejections_and_keeps_the_rest(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "requests.jsonl")
            bad_gold = dict(LINE_NA, id="ood-009", gold=gold(asked=["nonsense"]))
            write_lines(path, [LINE_NCA, "{not json", "", LINE_COMPARE, bad_gold, dict(LINE_NCA)])      # last: duplicate id of the first
            items, rejected = E.read_requests(path)
        self.assertEqual([it["row"]["id"] for it in items], ["ood-001", "ood-002"])
        self.assertEqual([(r["line"], r["id"]) for r in rejected], [(2, None), (5, "ood-009"), (6, "ood-001")])
        self.assertIn("not valid JSON", rejected[0]["reason"]); self.assertIn("unknown parameter key", rejected[1]["reason"])
        self.assertIn("duplicate id", rejected[2]["reason"])
        rep = E.schema_report(items, rejected)
        self.assertIn("Lines converted: 2. Lines rejected: 3", rep); self.assertIn("ood-009", rep)

    def test_rows_file_roundtrip(self):
        items = convert(*LINES)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "rows.jsonl"); E.write_rows(items, path)
            with open(path, encoding="utf-8") as f: rows = [json.loads(l) for l in f]
        self.assertEqual([r["id"] for r in rows], ["ood-001", "ood-002", "ood-003"])
        self.assertEqual(set(rows[0]), set(md.build_row(META, CSV, True, "compare", 0, None, random.Random(0))))


class TestMajority(unittest.TestCase):
    def rows(self):
        return [{"gold": json.dumps({"a": {"label": "x"}, "b": {"label": "true"}})},
                {"gold": json.dumps({"a": {"label": "y"}, "b": {"label": "true"}})},
                {"gold": json.dumps({"a": {"label": "y"}, "b": {"label": "false"}})},
                {"gold": json.dumps({"a": {"label": "x"}, "b": {"label": "false"}})}]

    def test_most_frequent_label_with_alphabetical_ties(self):
        self.assertEqual(E.majority_labels(self.rows()), {"a": "x", "b": "false"})
        self.assertEqual(E.majority_labels(self.rows()[:3]), {"a": "y", "b": "true"})

    def test_majority_decider_answers_the_learned_labels(self):
        d = E.majority_decider({"analysis": "none_needed"})
        out = d({}, {"analysis": {"type": "choice", "criteria": {"nca": "", "none_needed": ""}},
                     "route": {"type": "choice", "criteria": {"oral": "", "unknown": ""}}})
        self.assertEqual(out, {"analysis": "none_needed", "route": "oral"})                  # unknown question: first option

    def test_majority_of_the_real_training_rows_when_present(self):
        if not os.path.isfile(E.TRAIN): self.skipTest("decision/data/train.jsonl is not built")
        labels = E.load_train_majority(regenerate=False)
        self.assertEqual(labels["analysis"], "none_needed"); self.assertEqual(labels["asked_tlag"], "false")

    def test_train_majority_from_a_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "train.jsonl"); md.write(self.rows(), path)
            self.assertEqual(E.load_train_majority(path, regenerate=False), {"a": "x", "b": "false"})


class Fake:
    """A decider that answers the gold labels, except the listed (row id -> {question: label}); gives probabilities like the trained one."""
    def __init__(self, rows, wrong=None, probs=True):
        self.gold = {json.dumps(json.loads(r["state"]), sort_keys=True): (r["id"], {q: g["label"] for q, g in json.loads(r["gold"]).items()}) for r in rows}
        self.wrong, self.probs, self.last_info = wrong or {}, probs, None
    def __call__(self, state, questions):
        rid, labels = self.gold[json.dumps(state, sort_keys=True)]
        labels = {**labels, **self.wrong.get(rid, {})}
        if self.probs:
            self.last_info = {"seconds": 0.0, "answers": {q: {"label": l, "confidence": 0.9, "probabilities": {l: 0.9, "other": 0.1}}
                                                          for q, l in labels.items()}}
        return labels


class TestScoring(unittest.TestCase):
    def setUp(self):
        self.items = convert(*LINES); self.rows = [it["row"] for it in self.items]
        self.tag_of = {it["row"]["id"]: it["tags"] for it in self.items}
        self.request_of = {it["row"]["id"]: it["request"] for it in self.items}

    def test_gold_is_one_hundred_percent(self):
        res, probs = E.score_rows(self.rows, E.RowDecider("gold"))
        per, tot = E.z.accuracy(res)
        self.assertEqual(tot, (60, 60)); self.assertTrue(all(c == t for c, t in per.values())); self.assertFalse(probs)
        self.assertEqual(E.wrong_decisions(res, self.request_of), [])
        self.assertEqual(E.broken_tags(E.per_tag(res, self.tag_of), 1.0), [])

    def test_fake_decider_with_errors(self):
        fake = Fake(self.rows, wrong={"ood-001": {"route": "unknown", "asked_tmax": "false"}, "ood-003": {"is_not_available": "false"}})
        res, probs = E.score_rows(self.rows, fake)
        self.assertTrue(probs)
        per, tot = E.z.accuracy(res)
        self.assertEqual(tot, (57, 60)); self.assertEqual(per["route"], (2, 3)); self.assertEqual(per["is_not_available"], (2, 3))
        self.assertEqual(per["analysis"], (3, 3))
        wrong = E.wrong_decisions(res, self.request_of)
        self.assertEqual(sorted((w["id"], w["question"], w["gold"], w["pred"]) for w in wrong),
                         [("ood-001", "asked_tmax", "true", "false"), ("ood-001", "route", "oral", "unknown"), ("ood-003", "is_not_available", "true", "false")])
        self.assertTrue(all(w["request"] and w["confidence"] == 0.9 for w in wrong))
        self.assertEqual(E.off_diagonal(res, "route"), [("oral", "unknown", 1)])
        self.assertEqual(E.asked_errors(res), (1, 0, 4))                                      # tmax missed; cmax, auclast, c0 hit
        tags = E.per_tag(res, self.tag_of)
        self.assertEqual(tags["colloquial"], {"rows": 1, "correct": 18, "total": 20, "exact_rows": 0})
        self.assertEqual(tags["not-available"]["exact_rows"], 0); self.assertEqual(tags["compare-methods"]["exact_rows"], 1)
        self.assertEqual(E.broken_tags(tags, 1 / 3), ["abbreviation", "colloquial", "not-available", "typo"])
        table, ece = E.z.calibration(res)
        self.assertEqual(table[9]["n"], 60); self.assertAlmostEqual(table[9]["acc"], 57 / 60)

    def test_outside_options_is_a_wrong_label(self):
        fake = Fake(self.rows, wrong={"ood-003": {"compare_pair": "2+3"}}, probs=False)        # only one analysis there: 2+3 is not offered
        res, probs = E.score_rows(self.rows, fake)
        self.assertFalse(probs)
        w = E.wrong_decisions(res, self.request_of)
        self.assertEqual([(x["id"], x["question"], x["pred"], x["confidence"]) for x in w], [("ood-003", "compare_pair", "(outside options)", None)])

    def test_report_sections_and_baseline_column(self):
        fake = Fake(self.rows, wrong={"ood-001": {"route": "unknown"}})
        res, probs = E.score_rows(self.rows, fake)
        base, _ = E.score_rows(self.rows, E.majority_decider(E.majority_labels(self.rows)))
        text, scores, broke = E.score_section(res, probs, base, self.tag_of, self.request_of)
        for part in ("### Accuracy per question", "always-majority (these rows)", "majority (train.jsonl)", "### Confusions", "oral -> unknown (1)",
                     "### Accuracy per tag", "Tags that broke", "### Calibration", "Expected calibration error", "### Wrong decisions (1)",
                     self.request_of["ood-001"]):
            self.assertIn(part, text)
        self.assertEqual(scores["correct"], 59); self.assertEqual(scores["exact_rows"], 2); self.assertEqual(scores["per_question"]["route"]["total"], 3)
        self.assertEqual(broke, ["colloquial", "typo"])
        text2, _, _ = E.score_section(res, False, None, self.tag_of, self.request_of)
        self.assertIn("no calibration table", text2); self.assertIn("n/a", text2)

    def test_evaluate_writes_the_run_folder_without_the_engine(self):
        with tempfile.TemporaryDirectory() as tmp:
            train = os.path.join(tmp, "train.jsonl"); md.write(self.rows, train)
            folder, scores, records = E.evaluate(self.items, "gold", "2026-10-09", run=False, out_root=tmp, train_path=train)
            self.assertEqual(os.path.basename(folder), "2026-10-09-gold"); self.assertEqual(records, [])
            self.assertEqual(scores["correct"], scores["decisions"])
            text = read(os.path.join(folder, "report.md"))
            self.assertIn("100.0 %", text); self.assertIn("decider `gold`", text)
            folder, scores, _ = E.evaluate(self.items, "majority", "2026-10-09", run=False, out_root=tmp, train_path=train)
            self.assertEqual(os.path.basename(folder), "2026-10-09-majority"); self.assertLess(scores["accuracy"], 1.0)
            self.assertTrue(os.path.isfile(os.path.join(folder, "scores.json")))


class TestAnswerKinds(unittest.TestCase):
    def test_templates_are_classified(self):
        T = H
        self.assertEqual(E.answer_kind(T.T_ASK_ROUTE), "refusal:ask"); self.assertEqual(E.answer_kind(T.T_ASK_DOSE_UNIT), "refusal:ask")
        self.assertEqual(E.answer_kind(T.T_NO_DATA), "refusal:no-data"); self.assertEqual(E.answer_kind(T.T_NO_ANALYSIS), "refusal:no-analysis")
        self.assertEqual(E.answer_kind(T.T_NOT_WIRED.format(what="x")), "refusal:not-wired")
        self.assertEqual(E.answer_kind(T.T_NOT_SUPPORTED), "refusal:not-supported")      # 2026-10-10: was filed under not-wired
        self.assertEqual(E.answer_kind(T.T_NOT_WIRED.format(what="ajustement d'un modèle à un compartiment")), "refusal:not-wired")
        self.assertEqual(E.answer_kind(T.T_NO_PARAMETER), "refusal:no-parameter")
        self.assertEqual(E.answer_kind(T.T_UNDECIDED.format(qs="x")), "refusal:undecided")
        self.assertEqual(E.answer_kind(T.T_WHICH_PAIR.format(analyses="a")), "refusal:which-pair")
        self.assertEqual(E.answer_kind(T.T_TOOL_FAILED.format(tool="t", error="e")), "refusal:tool-failed")
        self.assertEqual(E.answer_kind(T.render_refusal("c0", None)), "refusal:not-available")
        self.assertEqual(E.answer_kind("Résultats de Caladrius (analyse 2) :\n- Cmax : 1 mg/L\nC0 n'est pas calculé par Caladrius."), "answer")

    def test_expected_refusal(self):
        base = {"is_not_available": "false", "analysis": "none_needed", "route": "oral", "dose_has_unit": "true"}
        self.assertFalse(E.expects_refusal(base))
        self.assertTrue(E.expects_refusal(dict(base, is_not_available="true")))
        self.assertTrue(E.expects_refusal(dict(base, analysis="nca", route="unknown")))
        self.assertTrue(E.expects_refusal(dict(base, analysis="nca", dose_has_unit="false")))
        self.assertTrue(E.expects_refusal(dict(base, analysis="fit_pk1")))
        self.assertTrue(E.expects_refusal(dict(base, analysis="not_supported")))

    def test_what_a_human_reads(self):
        rec = lambda i, kind, **kw: {"id": i, "exercise": EX, "turn": 1, "tags": ["t1"], "request": "r", "answer": "a", "answer_kind": kind,
                                     "expected_refusal": False, "wrong_decisions": {}, "state_matches_row": True, **kw}
        records = [rec("a", "answer"), rec("b", "answer", wrong_decisions={"route": {"gold": "oral", "pred": "unknown"}}),
                   rec("c", "refusal:ask"), rec("d", "answer", expected_refusal=True), rec("e", "error", error="boom"), rec("f", "answer", tags=["broken"])]
        out = {r["id"]: why for r, why in E.to_read(records, ["broken"])}
        self.assertEqual(sorted(out), ["b", "c", "d", "e", "f"])
        self.assertIn("wrong decision: route", out["b"][0]); self.assertIn("expect an answer", out["c"][0])
        self.assertIn("expect a refusal", out["d"][0]); self.assertIn("boom", out["e"][0]); self.assertIn("broke", out["f"][0])
        self.assertIn("1 refusals or questions back", E.run_section(records, ["broken"]))


@unittest.skipUnless(os.path.exists(apothicaire.MCP_BIN), "caladrius-mcp is not built (see apothicaire.MCP_BIN)")
class TestRealEngine(unittest.TestCase):
    def test_gold_decisions_through_the_harness(self):
        line_unknown = dict(LINE_NCA, id="ood-004", request="400 mg, je ne sais plus comment je l'ai pris. Donne-moi la Cmax.",
                            tags=["route-implied"], gold=gold(analysis="nca", auc_method="linear", route="unknown", asked=["cmax"]))
        items = convert(*LINES, line_unknown)
        with tempfile.TemporaryDirectory() as tmp:
            train = os.path.join(tmp, "train.jsonl"); md.write([it["row"] for it in items], train)
            folder, scores, records = E.evaluate(items, "gold", "2026-10-09", run=True, out_root=tmp, train_path=train)
            self.assertEqual(scores["correct"], scores["decisions"])
            by = {r["id"]: r for r in records}
            self.assertEqual({k: v["answer_kind"] for k, v in by.items()},
                             {"ood-001": "answer", "ood-002": "answer", "ood-003": "refusal:not-available", "ood-004": "refusal:ask"})
            self.assertIn("Cmax", by["ood-001"]["answer"]); self.assertNotIn("AUC(0", by["ood-001"]["answer"])
            self.assertIn("Comparaison calculée par Caladrius entre l'analyse 2 et l'analyse 3", by["ood-002"]["answer"])
            self.assertIn("C0", by["ood-003"]["answer"])
            for r in records:
                self.assertTrue(r["state_matches_row"], r["id"]); self.assertEqual(r["wrong_decisions"], {}); self.assertEqual(r["harness_notes"], [])
            self.assertEqual(by["ood-002"]["new_tool_calls"], ["analysis_compare"])               # the two analyses were replayed beforehand
            lines = [json.loads(l) for l in read(os.path.join(folder, "answers.jsonl")).splitlines()]
            self.assertEqual([l["id"] for l in lines], ["ood-001", "ood-002", "ood-003", "ood-004"])
            report = read(os.path.join(folder, "report.md"))
            self.assertIn("## What a human must read", report); self.assertIn("2 refusals or questions back", report)

    def test_prior_analyses_replayed_on_an_exercise_without_oracle(self):
        if not os.path.isfile(E.REQUESTS): self.skipTest("no decision/ood/requests.jsonl")
        items, rejected = E.read_requests()
        item = next((it for it in items if it["row"]["id"] == "ood-072"), None)           # compare of two prior analyses on oodx09_oral_min_ng (turn 2, no nca oracle)
        if item is None: self.skipTest("ood-072 not in requests.jsonl")
        self.assertFalse([r for r in rejected if r["id"] == "ood-072"])
        with tempfile.TemporaryDirectory() as tmp:
            train = os.path.join(tmp, "train.jsonl"); md.write([item["row"]], train)
            _, scores, records = E.evaluate([item], "gold", "2026-10-09", run=True, out_root=tmp, train_path=train)
        self.assertEqual(scores["correct"], scores["decisions"])
        self.assertEqual(records[0]["answer_kind"], "answer", records[0].get("error"))
        self.assertIn("Comparaison calculée par Caladrius", records[0]["answer"])
        self.assertEqual(records[0]["harness_notes"], [])


if __name__ == "__main__":
    unittest.main()
