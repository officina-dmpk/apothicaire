"""Tests of the zero-shot d1 baseline (decision/zero_shot_d1.py): conversion of a typed-decisions row to the `system_one` call, answer
normalisation, accuracy, confusion, calibration bins and the report, all on a synthetic row and a fake predictor. No model download, no
torch import.
"""
import json, os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(AGENT, "decision"))
import zero_shot_d1 as zs  # noqa: E402

STATE = {"analyses": [{"id": 2, "kind": "nca", "auc_method": "linear"}], "notes": [],
         "data": {"header": "time (h),conc (ng/mL)", "first_rows": ["0,0", "1,5.2"], "n_rows": 11, "n_subjects": 1},
         "request": "Quelle est la clairance ?", "user_dose_sentence": "Dose : 100 mg par voie orale."}
QUESTIONS = {
    "analysis": {"type": "choice", "instructions": "Which computation?", "criteria": {"nca": "Run an NCA.", "none_needed": "Nothing new."}},
    "parameter_asked": {"type": "choice", "instructions": "Which parameter?", "criteria": {"cl": "Clearance", "several": "Two or more", "none": "None"}},
    "dose_has_unit": {"type": "noul", "instructions": "The dose carries a unit.", "criteria": {"false": "No.", "true": "Yes."}},
}


def gold_entry(qtype, label, options):
    probs = {o: 1.0 if o == label else 0.0 for o in options}
    return {"type": qtype, "label": label, "confidence": 1.0, "probabilities": probs}


def make_row(i=0, analysis="none_needed", param="cl", unit="true"):
    gold = {"analysis": gold_entry("choice", analysis, ["nca", "none_needed"]),
            "parameter_asked": gold_entry("choice", param, ["cl", "several", "none"]),
            "dose_has_unit": dict(gold_entry("noul", unit, ["false", "true"]), noul=1.0 if unit == "true" else 0.0)}
    return {"id": "te_x_%06d" % i, "workflow": "w", "split": "test", "state": json.dumps(STATE, ensure_ascii=False),
            "questions": json.dumps(QUESTIONS), "gold": json.dumps(gold), "factors": "{}", "label_agreement": "{}", "n_questions": 3}


def fake_answers(call, choices, noul):
    """Answer of `model.system_one`'s shape: choices maps question -> (label, confidence), noul is P(true)."""
    out = {}
    for name, q in call.items():
        if q["type"] == "choice":
            label, conf = choices[name]
            others = [k for k in q["criteria"] if k != label]
            probs = {label: conf, **{k: (1 - conf) / len(others) for k in others}}
            out[name] = {"type": "choice", "choice": label, "confidence": conf, "probabilities": probs}
        else:
            out[name] = {"type": "noul", "noul": noul}
    return {"answers": out, "usage": {"input_tokens": 10, "output_tokens": 0}}


class Conversion(unittest.TestCase):
    def test_row_to_call(self):
        state, call, gold = zs.to_call(make_row())
        self.assertIsInstance(state, str)
        self.assertEqual(json.loads(state), STATE)
        self.assertIn("100 mg", state)
        self.assertIn("Quelle est la clairance", state)  # the request is in the state text
        self.assertEqual(list(call), ["analysis", "parameter_asked", "dose_has_unit"])
        self.assertEqual(call["analysis"], {"type": "choice", "instructions": "Which computation?",
                                            "criteria": {"nca": "Run an NCA.", "none_needed": "Nothing new."}})
        self.assertEqual(call["dose_has_unit"]["type"], "noul")
        self.assertEqual(call["dose_has_unit"]["instructions"], "The dose carries a unit.")
        self.assertEqual(call["dose_has_unit"]["criteria"], {"false": "No.", "true": "Yes."})
        for q in call.values(): self.assertEqual(set(q) - {"criteria"}, {"type", "instructions"})
        self.assertEqual(gold, {"analysis": "none_needed", "parameter_asked": "cl", "dose_has_unit": "true"})

    def test_noul_without_criteria_stays_without(self):
        row = make_row()
        qs = json.loads(row["questions"]); del qs["dose_has_unit"]["criteria"]; row["questions"] = json.dumps(qs)
        self.assertNotIn("criteria", zs.to_call(row)[1]["dose_has_unit"])

    def test_normalise(self):
        c = zs.normalise_answer({"type": "choice"}, {"type": "choice", "choice": "nca", "probabilities": {"nca": 0.7, "none_needed": 0.3}})
        self.assertEqual(c, {"label": "nca", "probs": {"nca": 0.7, "none_needed": 0.3}})
        n = zs.normalise_answer({"type": "noul"}, {"type": "noul", "noul": 0.2})
        self.assertEqual(n["label"], "false")
        self.assertAlmostEqual(n["probs"]["false"], 0.8); self.assertAlmostEqual(n["probs"]["true"], 0.2)
        self.assertEqual(zs.normalise_answer({"type": "noul"}, {"noul": 0.5})["label"], "true")
        with self.assertRaises(ValueError): zs.normalise_answer({"type": "score"}, {"score": 1.0})


def run_fake():
    """Three rows; the fake model is right on row 0, wrong on `analysis` of row 1, wrong on the noul of row 2."""
    rows = [make_row(0), make_row(1, analysis="nca", param="several"), make_row(2, analysis="none_needed", param="none", unit="false")]
    answers = [({"analysis": ("none_needed", 0.95), "parameter_asked": ("cl", 0.9)}, 0.99),
               ({"analysis": ("none_needed", 0.85), "parameter_asked": ("several", 0.6)}, 0.97),
               ({"analysis": ("none_needed", 0.55), "parameter_asked": ("none", 0.35)}, 0.9)]
    it = iter(answers)
    return zs.predict_rows(lambda state, call: fake_answers(call, *next(it)), rows)


class Metrics(unittest.TestCase):
    def test_predict_rows(self):
        res = run_fake()
        self.assertEqual([r["id"] for r in res], ["te_x_000000", "te_x_000001", "te_x_000002"])
        self.assertTrue(all(r["seconds"] >= 0 for r in res))
        self.assertEqual(res[1]["pred"]["analysis"]["label"], "none_needed")
        self.assertEqual(res[1]["gold"]["analysis"], "nca")

    def test_accuracy(self):
        per, tot = zs.accuracy(run_fake())
        self.assertEqual(per["analysis"], (2, 3))
        self.assertEqual(per["parameter_asked"], (3, 3))
        self.assertEqual(per["dose_has_unit"], (2, 3))  # row 2: gold false, P(true) 0.9 -> true
        self.assertEqual(tot, (7, 9))

    def test_majority(self):
        m = zs.majority(run_fake())
        self.assertEqual(m["analysis"], (2, 3)); self.assertEqual(m["dose_has_unit"], (2, 3)); self.assertEqual(m["parameter_asked"], (1, 3))

    def test_confusion(self):
        cm = zs.confusion(run_fake(), "analysis")
        self.assertEqual(cm, {"none_needed": {"none_needed": 2}, "nca": {"none_needed": 1}})

    def test_calibration_bins(self):
        res = run_fake()
        table, ece = zs.calibration(res)
        self.assertEqual(len(table), 10)
        self.assertEqual(sum(b["n"] for b in table), 9)
        # chosen-label probabilities: analysis .95 .85 .55; parameter .9 .6 .35; noul(.99 .97 .9 -> true) all 'true'
        counts = [b["n"] for b in table]
        self.assertEqual(counts, [0, 0, 0, 1, 0, 1, 1, 0, 1, 5])  # 0.35 | 0.55 | 0.6 | 0.85 | 0.95,0.9,0.9,0.99,0.97
        b9 = table[9]
        self.assertAlmostEqual(b9["mean_conf"], (0.95 + 0.9 + 0.99 + 0.97 + 0.9) / 5)
        self.assertAlmostEqual(b9["acc"], 4 / 5)  # the wrong one in the top bin is the noul of row 2
        self.assertEqual(table[3]["acc"], 1.0)    # 0.35 in bin 3: parameter 'none' was right
        self.assertEqual(table[5]["acc"], 1.0)    # 0.55: analysis of row 2, right
        self.assertEqual(table[8]["acc"], 0.0)    # 0.85: analysis of row 1, wrong
        self.assertIsNone(table[0]["mean_conf"])
        ece_by_hand = sum(b["n"] * abs(b["mean_conf"] - b["acc"]) for b in table if b["n"]) / 9
        self.assertAlmostEqual(ece, ece_by_hand)

    def test_probability_one_goes_to_last_bin(self):
        self.assertEqual(zs.bin_index(1.0), 9)
        self.assertEqual(zs.bin_index(0.0), 0)
        self.assertEqual(zs.bin_index(0.1), 1)
        self.assertEqual(zs.bin_index(0.999), 9)

    def test_calibration_filtered_by_question(self):
        table, _ = zs.calibration(run_fake(), {"dose_has_unit"})
        self.assertEqual(sum(b["n"] for b in table), 3)

    def test_timing(self):
        t = zs.timing([{"seconds": 0.01}, {"seconds": 0.03}, {"seconds": 0.02}])
        self.assertAlmostEqual(t["mean_ms"], 20.0); self.assertAlmostEqual(t["median_ms"], 20.0)


class Report(unittest.TestCase):
    def test_report_from_run_file(self):
        res = run_fake()
        meta = {"model": "d1-fake", "split": "heldout", "limit": None, "n_rows": 3, "device": "cpu", "dtype": "float32", "load_s": 1.0,
                "wall_s": 0.5, "warmup_rows": 0, "python": "3.12", "torch": "x", "transformers": "y", "gpu": None, "vram_text": "none (cpu)"}
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "d1-fake-heldout.json"), "w", encoding="utf-8") as f: json.dump({"meta": meta, "rows": res}, f)
            path = zs.write_report(d)
            with open(path, encoding="utf-8") as f: text = f.read()
        for s in ("## d1-fake, heldout", "**overall**", "77.8 %", "Confusion: analysis", "Confusion: parameter_asked",
                  "Calibration", "Expected calibration error", "ms per row", "Time per row", "always-majority"):
            self.assertIn(s, text)
        self.assertEqual(zs.write_report(tempfile.gettempdir() + os.sep + "no-such-run-folder-d1"), None)

    def test_notes_are_appended_and_stride_spreads_rows(self):
        meta = {"model": "d1-fake", "split": "bench", "limit": 2, "stride": 4, "n_rows": 2, "device": "cpu", "dtype": "float32",
                "load_s": 1.0, "wall_s": 0.5, "python": "3.12", "torch": "x", "transformers": "y", "gpu": None}
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "d1-fake-bench-limit2-stride4.json"), "w", encoding="utf-8") as f: json.dump({"meta": meta, "rows": run_fake()}, f)
            with open(os.path.join(d, "notes.md"), "w", encoding="utf-8") as f: f.write("## Notes\n\nA remark.\n")
            path = zs.write_report(d)
            with open(path, encoding="utf-8") as f: text = f.read()
            self.assertIn("(every 4th)", text); self.assertTrue(text.rstrip().endswith("A remark."))
            rows_path = os.path.join(d, "rows.jsonl")
            with open(rows_path, "w", encoding="utf-8") as f: f.write("".join(json.dumps(make_row(i)) + "\n" for i in range(10)))
            self.assertEqual([r["id"] for r in zs.load_rows(rows_path, limit=3, stride=4)], ["te_x_000000", "te_x_000004", "te_x_000008"])
            self.assertEqual(len(zs.load_rows(rows_path)), 10)

    def test_dataset_row_is_convertible(self):
        """First row of the real held-out file, when it has been generated (decision/make_dataset.py)."""
        path = os.path.join(AGENT, "decision", "data", "heldout.jsonl")
        if not os.path.exists(path): self.skipTest("decision/data/heldout.jsonl not generated")
        rows = zs.load_rows(path, limit=3)
        self.assertEqual(len(rows), 3)
        for row in rows:
            state, call, gold = zs.to_call(row)
            self.assertEqual(set(call), set(gold))
            for name, q in call.items():
                self.assertIn(q["type"], ("choice", "noul"))
                if q["type"] == "choice": self.assertIn(gold[name], q["criteria"])


if __name__ == "__main__":
    unittest.main()
