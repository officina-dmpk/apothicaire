"""Tests of decision/train_unsloth.py and decision/predict_unsloth.py: jsonl -> Hugging Face dataset conversion, spread sampling, argument
parsing, run naming. No model download, no GPU, no import of unsloth itself (the data and argument helpers do not need it); skipped when
the test interpreter has no `datasets` package (the Unsloth venv has it: .venv-unsloth/Scripts/python -m unittest tests.test_train_unsloth).
"""
import json, os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(AGENT, "decision"))

try:
    import datasets  # noqa: F401
    HAVE_DATASETS = True
except ImportError:
    HAVE_DATASETS = False

import train_unsloth as tu  # noqa: E402  (stdlib only at import time)
import predict_unsloth as pu  # noqa: E402
import decider_unsloth as du  # noqa: E402  (torch and unsloth are imported lazily, at the first decide call)

STATE = {"analyses": [], "data": {"header": "time (h),conc (mg/L)", "n_rows": 11}, "request": "Cmax ?"}
QUESTIONS = {"analysis": {"type": "choice", "instructions": "Which computation?", "criteria": {"nca": "NCA", "none_needed": "none"}},
             "asked_cmax": {"type": "noul", "instructions": "Is Cmax asked?", "criteria": {"false": "no", "true": "yes"}}}
GOLD = {"analysis": {"type": "choice", "label": "nca", "confidence": 1.0, "probabilities": {"nca": 1.0, "none_needed": 0.0}},
        "asked_cmax": {"type": "noul", "label": "true", "confidence": 1.0, "noul": 1.0, "probabilities": {"false": 0.0, "true": 1.0}}}


def make_row(i, split="train"):
    return {"id": "tr_x_%06d" % i, "workflow": "pk_analysis_requests", "split": split, "state": json.dumps(STATE, sort_keys=True),
            "questions": json.dumps(QUESTIONS, sort_keys=True), "gold": json.dumps(GOLD, sort_keys=True),
            "factors": json.dumps({"exercise": i // 10}), "label_agreement": "{}", "n_questions": 2}


def write_jsonl(folder, name, n):
    with open(os.path.join(folder, name + ".jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for i in range(n): f.write(json.dumps(make_row(i), ensure_ascii=False) + "\n")


class TestSpread(unittest.TestCase):
    def test_no_limit_keeps_everything(self):
        rows = list(range(10))
        self.assertEqual(tu.spread(rows), rows)
        self.assertEqual(tu.spread(rows, 10), rows)
        self.assertEqual(tu.spread(rows, 50), rows)

    def test_even_spacing_and_count(self):
        out = tu.spread(list(range(100)), 10)
        self.assertEqual(out, [0, 10, 20, 30, 40, 50, 60, 70, 80, 90])
        self.assertEqual(len(tu.spread(list(range(7)), 3)), 3)
        self.assertEqual(len(set(tu.spread(list(range(1000)), 200))), 200)

    def test_deterministic(self):
        self.assertEqual(tu.spread(list(range(333)), 17), tu.spread(list(range(333)), 17))


@unittest.skipUnless(HAVE_DATASETS, "datasets is not installed in this interpreter")
class TestDataset(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        write_jsonl(self.tmp.name, "train", 30)
        write_jsonl(self.tmp.name, "heldout", 12)

    def test_read_jsonl(self):
        rows = tu.read_jsonl(os.path.join(self.tmp.name, "train.jsonl"))
        self.assertEqual(len(rows), 30)
        self.assertEqual(rows[3]["id"], "tr_x_000003")

    def test_conversion_keeps_the_typed_decisions_columns(self):
        ds = tu.load_split("train", data_dir=self.tmp.name)
        self.assertEqual(len(ds), 30)
        self.assertEqual(set(ds.column_names), {"id", "workflow", "split", "state", "questions", "gold", "n_questions"})
        row = ds[0]
        self.assertIsInstance(row["state"], str)  # JSON text, as in the Hub dataset: build_dataset parses it itself
        self.assertEqual(json.loads(row["questions"]), QUESTIONS)
        self.assertEqual(json.loads(row["gold"])["analysis"]["label"], "nca")

    def test_limit_spreads_over_the_file(self):
        ds = tu.load_split("train", 6, data_dir=self.tmp.name)
        self.assertEqual(len(ds), 6)
        self.assertEqual([r["id"] for r in ds], ["tr_x_%06d" % i for i in (0, 5, 10, 15, 20, 25)])

    def test_question_names_follow_the_rows(self):
        ds = tu.load_split("heldout", data_dir=self.tmp.name)
        self.assertEqual(tu.question_names(ds), ["analysis", "asked_cmax"])
        # a row that declares another question is picked up without any change of the code
        row = make_row(99); q = json.loads(row["questions"]); q["asked_tlag"] = q["asked_cmax"]; row["questions"] = json.dumps(q)
        self.assertEqual(tu.question_names(tu.to_dataset([row])), ["analysis", "asked_cmax", "asked_tlag"])

    def test_real_files_if_present(self):
        path = os.path.join(tu.DATA, "train.jsonl")
        if not os.path.exists(path): self.skipTest("decision/data/train.jsonl not generated")
        ds = tu.load_split("train", 20)
        self.assertEqual(len(ds), 20)
        for row in ds:
            q, g = json.loads(row["questions"]), json.loads(row["gold"])
            self.assertEqual(set(q), set(g))


class TestArguments(unittest.TestCase):
    def test_defaults_follow_the_recipe(self):
        a = tu.parse_args([])
        self.assertEqual((a.base, a.epochs, a.batch_size, a.grad_accum, a.lr, a.max_seq_length), ("unsloth/Qwen3.5-0.8B", 2.0, 8, 4, 2e-4, 2048))
        self.assertIsNone(a.limit); self.assertFalse(a.no_4bit)
        self.assertEqual(os.path.normpath(a.out), os.path.normpath(os.path.join(tu.MODELS, "qwen3.5-0.8b-decisions")))

    def test_flags(self):
        a = tu.parse_args(["--base", "unsloth/Qwen3.5-2B", "--epochs", "3", "--batch-size", "4", "--grad-accum", "8", "--lr", "1e-4",
                           "--limit", "200", "--eval-limit", "100", "--out", "somewhere", "--no-4bit", "--max-steps", "5"])
        self.assertEqual((a.base, a.epochs, a.batch_size, a.grad_accum, a.lr), ("unsloth/Qwen3.5-2B", 3.0, 4, 8, 1e-4))
        self.assertEqual((a.limit, a.eval_limit, a.out, a.no_4bit, a.max_steps), (200, 100, "somewhere", True, 5))

    def test_out_folder_is_named_after_the_base_model(self):
        a = tu.parse_args(["--base", "unsloth/Qwen3.5-2B/"])
        self.assertTrue(a.out.endswith("qwen3.5-2b-decisions"))

    def test_models_folder_is_git_ignored(self):
        with open(os.path.join(AGENT, ".gitignore"), encoding="utf-8") as f:
            self.assertIn("decision/models/", f.read().split())

    def test_predict_arguments_and_names(self):
        a = pu.parse_args(["--model", "decision/models/run1/merged", "--split", "bench", "--limit", "10", "--stride", "3", "--device", "cpu"])
        self.assertEqual((a.split, a.limit, a.stride, a.device, a.load_in_4bit), ("bench", 10, 3, "cpu", False))
        self.assertEqual(pu.model_name(os.path.join("decision", "models", "run1", "merged")), "run1-merged")
        self.assertEqual(pu.model_name(os.path.join("somewhere", "mymodel")), "mymodel")
        self.assertEqual(pu.run_name("run1-merged", "heldout", 100, 7, "cuda"), "unsloth-run1-merged-heldout-limit100-stride7-cuda")
        self.assertEqual(pu.run_name("m", "/x/y/rows.jsonl", None, 1, "cpu"), "unsloth-m-rows-cpu")

    def test_predict_split_path(self):
        self.assertTrue(pu.split_path("heldout").endswith(os.path.join("data", "heldout.jsonl")))
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f: name = f.name
        try: self.assertEqual(pu.split_path(name), name)
        finally: os.unlink(name)


class TestPredictUsesTheD1Metrics(unittest.TestCase):
    def test_answers_of_unsloth_normalise_like_d1(self):
        q = QUESTIONS["analysis"]
        ans = {"type": "choice", "choice": "nca", "confidence": 0.8, "probabilities": {"nca": 0.9, "none_needed": 0.1}, "answer": "nca"}
        self.assertEqual(pu.z.normalise_answer(q, ans)["label"], "nca")
        noul = pu.z.normalise_answer(QUESTIONS["asked_cmax"], {"type": "noul", "noul": 0.2, "answer": False, "probabilities": {"true": 0.2, "false": 0.8}})
        self.assertEqual(noul["label"], "false"); self.assertAlmostEqual(noul["probs"]["false"], 0.8)


class TestDecider(unittest.TestCase):
    def test_labels_and_confidences_from_predict_answers(self):
        answers = {"analysis": {"type": "choice", "choice": "nca", "probabilities": {"nca": 0.7, "none_needed": 0.3}, "answer": "nca"},
                   "asked_cmax": {"type": "noul", "noul": 0.2, "answer": False, "probabilities": {"true": 0.2, "false": 0.8}}}
        labels, info = du.labels_of(QUESTIONS, answers)
        self.assertEqual(labels, {"analysis": "nca", "asked_cmax": "false"})
        self.assertEqual(info["analysis"]["confidence"], 0.7)
        self.assertEqual(info["asked_cmax"]["confidence"], 0.8)
        self.assertEqual(info["asked_cmax"]["probabilities"], {"false": 0.8, "true": 0.2})

    def test_noul_threshold_and_choice_without_choice_key(self):
        answers = {"analysis": {"type": "choice", "probabilities": {"nca": 0.4, "none_needed": 0.6}},
                   "asked_cmax": {"type": "noul", "noul": 0.5}}
        labels, _ = du.labels_of(QUESTIONS, answers)
        self.assertEqual(labels, {"analysis": "none_needed", "asked_cmax": "true"})

    def test_labels_pass_the_harness_normalisation(self):
        import harness
        labels, _ = du.labels_of(QUESTIONS, {"analysis": {"probabilities": {"nca": 0.9, "none_needed": 0.1}},
                                             "asked_cmax": {"noul": 0.9}})
        out, outside = harness.normalize_answers(labels, QUESTIONS)
        self.assertEqual((out, outside), ({"analysis": "nca", "asked_cmax": "true"}, []))


class TestBaselineSection(unittest.TestCase):
    def test_lists_the_questions_not_above_their_majority(self):
        def row(g, p): return {"gold": {"q1": g, "q2": g}, "pred": {"q1": {"label": p, "probs": {p: 1.0}}, "q2": {"label": g, "probs": {g: 1.0}}}}
        res = [row("a", "a"), row("a", "a"), row("a", "a"), row("b", "a")]    # q1: always "a" = the majority (3/4); q2: perfect (4/4)
        text = pu.baseline_section(res)
        self.assertIn("| q1 |", text); self.assertNotIn("| q2 |", text)


if __name__ == "__main__":
    unittest.main()
