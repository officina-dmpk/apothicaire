"""Tests of decision/ablation.py (row transformation, comparison, a run with a fake decider) and of the model selection of
decision/decider_unsloth.py ($D01_MODEL, run-folder name) used by eval_ood.py --model. No model, no GPU."""
import json, os, random, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(AGENT, "decision"))

import ablation as ab  # noqa: E402
import decider_unsloth as du  # noqa: E402
import eval_ood  # noqa: E402

STATE = {"analyses": [{"auc_method": "linear", "id": 2, "kind": "nca"}],
         "data": {"first_rows": ["0,0", "0.5,12.5", "1,40.25", "2,22", "4,BLQ"], "header": "time (h),conc (ng/mL)", "n_rows": 11, "n_subjects": 1},
         "notes": ["BLQ note"], "request": "Quelle est la Cmax ?", "user_dose_sentence": "Dose 100 mg par voie orale"}
QUESTIONS = {"analysis": {"type": "choice", "instructions": "Which?", "criteria": {"nca": "NCA", "none_needed": "none"}},
             "asked_cmax": {"type": "noul", "instructions": "Cmax asked?", "criteria": {"false": "no", "true": "yes"}}}
GOLD = {"analysis": {"type": "choice", "label": "none_needed", "confidence": 1.0, "probabilities": {"nca": 0.0, "none_needed": 1.0}},
        "asked_cmax": {"type": "noul", "label": "true", "confidence": 1.0, "noul": 1.0, "probabilities": {"false": 0.0, "true": 1.0}}}


def row(i, state=STATE):
    return {"id": "te_x_%06d" % i, "state": json.dumps(state, sort_keys=True), "questions": json.dumps(QUESTIONS, sort_keys=True),
            "gold": json.dumps(GOLD, sort_keys=True)}


def fake_decider(read_table):
    """Answers from the words alone; with read_table it flips `asked_cmax` when the digest holds a concentration above 30."""
    def decide(state, questions):
        flip = read_table and "data" in state and any(float(r.split(",")[1]) > 30 for r in state["data"]["first_rows"] if r.split(",")[1] != "BLQ")
        out = {"analysis": "none_needed", "asked_cmax": "false" if flip else "true"}
        decide.last_info = {"answers": {q: {"probabilities": ({"nca": 0.0, "none_needed": 1.0} if q == "analysis" else
                                                              {"false": 0.9 if flip else 0.1, "true": 0.1 if flip else 0.9})} for q in questions}}
        return {q: out[q] for q in questions}
    decide.last_info = None
    return decide


class TestTransform(unittest.TestCase):
    def test_none_is_a_copy(self):
        out = ab.transform_state(STATE, "none")
        self.assertEqual(out, STATE); self.assertIsNot(out, STATE)

    def test_random_conc_keeps_everything_but_the_concentrations(self):
        out = ab.random_concentrations(STATE, random.Random(1))
        self.assertEqual({k: v for k, v in out.items() if k != "data"}, {k: v for k, v in STATE.items() if k != "data"})
        self.assertEqual(out["data"]["header"], STATE["data"]["header"]); self.assertEqual(out["data"]["n_rows"], 11)
        old, new = [r.split(",") for r in STATE["data"]["first_rows"]], [r.split(",") for r in out["data"]["first_rows"]]
        self.assertEqual([c[0] for c in old], [c[0] for c in new])            # times untouched
        self.assertEqual(new[4][1], "BLQ")                                     # a non-number stays
        self.assertNotEqual([c[1] for c in old[:4]], [c[1] for c in new[:4]])
        for c in new[:4]: self.assertTrue(0.0 <= float(c[1]) <= 40.25)         # same magnitude: between 0 and the digest's largest value

    def test_random_conc_is_deterministic_per_row(self):
        rows = [row(1), row(2)]
        a, b = ab.transform_rows(rows, "random_conc", seed=7), ab.transform_rows(list(reversed(rows)), "random_conc", seed=7)
        self.assertEqual(a[0]["state"], b[1]["state"]); self.assertEqual(a[1]["state"], b[0]["state"])
        self.assertNotEqual(a[0]["state"], a[1]["state"])
        self.assertNotEqual(a[0]["state"], ab.transform_rows(rows, "random_conc", seed=8)[0]["state"])

    def test_no_table_removes_data_only(self):
        out = ab.transform_rows([row(1)], "no_table")[0]
        state = json.loads(out["state"])
        self.assertNotIn("data", state)
        self.assertEqual({k: v for k, v in state.items()}, {k: v for k, v in STATE.items() if k != "data"})
        self.assertEqual(out["gold"], row(1)["gold"]); self.assertEqual(out["questions"], row(1)["questions"]); self.assertEqual(out["id"], row(1)["id"])

    def test_state_without_digest(self):
        s = {k: v for k, v in STATE.items() if k != "data"}
        self.assertEqual(ab.random_concentrations(s, random.Random(0)), s)
        self.assertEqual(ab.drop_table(s), s)

    def test_unknown_mode(self):
        with self.assertRaises(ValueError): ab.transform_state(STATE, "shuffle")


class TestRun(unittest.TestCase):
    rows = [row(1), row(2), row(3)]

    def score(self, decide, mode):
        return eval_ood.score_rows(ab.transform_rows(self.rows, mode), decide)[0]

    def test_words_only_decider_does_not_move(self):
        d = fake_decider(False)
        base = self.score(d, "none")
        for mode in ("random_conc", "no_table"):
            c = ab.compare(base, self.score(d, mode))
            self.assertTrue(all(v["flips"] == 0 and v["mean_dp"] == 0 and v["acc_other"] == 1.0 for v in c.values()))

    def test_table_reading_decider_flips(self):
        d = fake_decider(True)
        base = self.score(d, "none")                                         # a 40.25 in every digest: flips asked_cmax to false (wrong)
        self.assertEqual(sum(r["pred"]["asked_cmax"]["label"] == "true" for r in base), 0)
        c = ab.compare(base, self.score(d, "no_table"))
        self.assertEqual(c["asked_cmax"]["flips"], 3); self.assertEqual(c["asked_cmax"]["acc_base"], 0.0); self.assertEqual(c["asked_cmax"]["acc_other"], 1.0)
        self.assertAlmostEqual(c["asked_cmax"]["mean_dp"], 0.8); self.assertEqual(c["analysis"]["flips"], 0)

    def test_main_with_fake_decider(self):
        with tempfile.TemporaryDirectory() as t:
            path = os.path.join(t, "rows.jsonl")
            with open(path, "w", encoding="utf-8") as f:
                for r in self.rows: f.write(json.dumps(r) + "\n")
            sys.modules["fake_ablation_decider"] = type(sys)("fake_ablation_decider")
            sys.modules["fake_ablation_decider"].decide = fake_decider(False)
            ab.main(["--decider", "fake_ablation_decider:decide", "--split", path, "--out-dir", t])
            md = [n for n in os.listdir(t) if n.endswith(".md")][0]
            text = open(os.path.join(t, md), encoding="utf-8").read()
            self.assertIn("| no_table |", text); self.assertIn("0 / 6", text)


class TestModelSelection(unittest.TestCase):
    def test_default(self):
        self.assertEqual(du.model_path({}), du.DEFAULT_MODEL)
        self.assertEqual(du.model_label(du.DEFAULT_MODEL), "qwen35-0.8b")

    def test_env_model_folder_and_label(self):
        with tempfile.TemporaryDirectory() as t:
            run = os.path.join(t, "qwen35-0.8b-d01-v2"); os.makedirs(os.path.join(run, "merged"))
            self.assertEqual(du.model_path({"D01_MODEL": run}), os.path.join(run, "merged"))       # the parent folder is accepted
            self.assertEqual(du.model_path({"D01_MODEL": os.path.join(run, "merged")}), os.path.join(run, "merged"))
            self.assertEqual(du.model_label(os.path.join(run, "merged")), "qwen35-0.8b-d01-v2")
            self.assertNotEqual(du.model_label(os.path.join(run, "merged")), du.model_label(du.DEFAULT_MODEL))

    def test_adapters_folder(self):
        with tempfile.TemporaryDirectory() as t:
            run = os.path.join(t, "run-x"); os.makedirs(os.path.join(run, "merged")); os.makedirs(os.path.join(run, "adapters"))
            ad = os.path.join(run, "adapters")
            self.assertEqual(du.model_path({"D01_MODEL": ad}), ad)                                   # an explicit adapters folder is kept
            self.assertTrue(du.is_adapters(ad)); self.assertFalse(du.is_adapters(os.path.join(run, "merged")))
            self.assertEqual(du.model_label(ad), "run-x-adapters")
            self.assertNotEqual(du.model_label(ad), du.model_label(os.path.join(run, "merged")))

    def test_eval_ood_names_the_run_after_the_model(self):
        old = os.environ.get("D01_MODEL")
        try:
            with tempfile.TemporaryDirectory() as t:
                os.environ["D01_MODEL"] = os.path.join(t, "my-model", "merged")
                decide, name = eval_ood.load_decider("decider_unsloth:decide")
                self.assertEqual(name, "my-model")
                del os.environ["D01_MODEL"]
                self.assertEqual(eval_ood.load_decider("decider_unsloth:decide")[1], "qwen35-0.8b")
        finally:
            if old is None: os.environ.pop("D01_MODEL", None)
            else: os.environ["D01_MODEL"] = old


if __name__ == "__main__":
    unittest.main()
