# Decision-model dataset (D-01, step 1)

Training data for a decision model that answers closed questions about the state of a PK-analysis conversation (see `PLAN.md`). Synthetic
data only: the exercises are simulated by Caladrius, nothing comes from coursework or from `private/`.

## Row schema (found on 2026-10-09)

Queried on 2026-10-09 from `https://datasets-server.huggingface.co/rows?dataset=LocalLLaMA%2Ftyped-decisions&config=all&split=train&offset=0&length=3`
(and `/info`): subset `all`, splits `train` (1200 rows) and `test` (400 rows). One row = one state and several closed questions. Columns, all
strings except `n_questions`:

| column | content |
|---|---|
| `id` | `tr_<workflow>_<000000>` (train), `te_...` (test) |
| `workflow` | name of the scenario, e.g. `customer_service` |
| `split` | `train` or `test` |
| `state` | JSON text (sorted keys) describing the situation |
| `questions` | JSON object `{name: {"type", "instructions", "criteria"}}`; `type` is `choice` (criteria: option key -> description), `noul` (criteria: `{"false": ..., "true": ...}`, the instruction is a statement) or `score` (criteria: list of level descriptions) |
| `gold` | JSON object `{name: {...}}`: `choice` -> `{"type","label","confidence","probabilities"}`; `noul` -> same plus `"noul"` (probability of true), labels `"false"`/`"true"`; `score` -> same plus `"score"` (expected level), label = the level index as a string |
| `factors` | JSON object, the hidden variables the generator used |
| `label_agreement` | JSON object `{name: {"argmax_agree", "argmax_majority", "total_variation"}}`, agreement between annotators |
| `n_questions` | integer, number of questions of the row |

In the Hugging Face data `gold` is a soft label (probabilities from several annotators, `confidence = (p_max - 1/K) / (1 - 1/K)`). Ours is
one-hot (the truth is known), so `confidence` is 1.0 and `label_agreement` is trivially in agreement (`total_variation` 0).
Unsloth was not installed here, so `FastDecisionModel.build_dataset` itself was not run on these files; the schema is the one of the dataset it reads.
Our `split` values are `train` and `test` (the file `heldout.jsonl` holds the `test` rows).

## Our rows

`workflow` = `pk_analysis_requests`, 20 questions per row (6 + one `asked_<key>` per parameter, 14), no `score` question (nothing in the closed set is graded). `state` is a digest of
what the harness knows at one turn:

```
{"analyses": [{"id": 2, "kind": "nca", "auc_method": "linear"}, ...],      // analyses already in the project
 "data": {"header": "time (h),conc (ng/mL)", "first_rows": [5 rows], "n_rows": 11, "n_subjects": 1},
 "notes": ["BLQ sentence of the user", ...],
 "request": "the question text of the turn",
 "user_dose_sentence": "the dose / route / units sentence as the user wrote it"}
```

| question | type | answers | gold comes from |
|---|---|---|---|
| `analysis` | choice | nca, fit_pk1, fit_pk2, simulate, compare, none_needed | turn kind: `import_nca` -> nca; `compare` -> compare; fit/simulate kinds; every question about a result already computed (and the recall, and the not-available question) -> none_needed |
| `route` | choice | iv_bolus, iv_infusion, oral, unknown | `meta.json` route; `unknown` when the sentence omits it |
| `auc_method` | choice | linear, lin_up_log_down, not_applicable | the method the request specifies or requires: linear (turn 1), lin_up_log_down (compare turn), else not_applicable |
| `asked_<key>` (14 questions: `asked_cmax`, `asked_tmax`, `asked_c0`, `asked_auclast`, `asked_aucinf`, `asked_lambda_z`, `asked_half_life`, `asked_cl`, `asked_vz`, `asked_mrt`, `asked_aucpext`, `asked_lambda_z_points`, `asked_adj_r2`, `asked_tlag`) | noul | false, true | true when the wording of the turn names that parameter ("The last request asks for ..."). One boolean per parameter, so a request for two or nine parameters has two or nine true answers. All false on a recall, a fit and a simulation (the fit parameters are model parameters, not NCA ones). The turn that asks for a parameter Caladrius does not compute for the route (`not_available`) has that one parameter true (C0 or Tlag). The first request of the benchmark (`import_nca`) has the nine it names true: Cmax, Tmax, AUC(0-tlast), AUC(0-inf), lambda_z, t1/2, CL, Vz, MRT |
| `dose_has_unit` | noul | false, true | whether the dose sentence carries mg / ug |
| `is_not_available` | noul | false, true | true exactly for the `not_available` kind: the parameter asked (C0 after an oral dose, Tlag or C0 after an IV dose) is in `ground_truth.nca.linear.not_calculated` of `meta.json` |
| `compare_pair` | choice | `not_applicable` and one key `a+b` per pair of analysis ids present (`2+3`); `none_available` when fewer than two analyses exist | true only on the compare turn |

Turn kinds: the 8 scripted ones of `bench/scripts.py` (import_nca, cmax_tmax, clearance_volume, half_life, lambda_z_regression, recall,
compare, not_available) and 4 extra kinds written for this dataset so that every option of `analysis` has examples and every parameter is asked by some turn:
`nca_other` (AUC(0-inf), MRT, AUC(0-tlast), lambda_z read from the NCA already run), `fit_pk1`, `fit_pk2`, `simulate`.

Per (exercise, kind): the scripted wording (scripted kinds only, verbatim from `bench/scripts.py`) and 2 hand-written French paraphrases
(3 for the extra kinds), picked among 4 to 5 wordings per kind (`WORDINGS` in `make_dataset.py`), some of which ask one parameter only.
Paraphrased rows also use 5 hand-written introductions of the data, 3 phrasings of each route, and in 20 % of them drop the unit of the
dose, in 20 % the route (not on `not_available` rows, where the route decides the answer). Conventions of the state: the compare turn is
described after the harness ran the requested re-run (analyses 2 and 3 present); in 40 % of the rows of the result-reading kinds both
analyses are present too (the question comes later in the conversation); a `simulate` state holds a fit as analysis 3.

## Exercises and split

- `bench/exercises/`: the 25 benchmark exercises (read only here). All of them go to `bench.jsonl` (`split` = `bench`, ids `be_...`,
  `factors.bench = true`). That file is never used for training or calibration: it is the comparison set against the 27B pipeline (step 5).
- `decision/exercises/`: 75 more, 3 seeds (31415926, 27182818, 16180339) of the same plan, generated by `decision/make_exercises.py`
  with `bench/make_exercises.py` (the benchmark seed is 20261009; a draw the oracle rejects is redrawn, see `meta.json` `attempt`).
- Split by exercise, never by row: 20 whole exercises drawn with seed 20261010 among the 75 new ones are `heldout.jsonl` (`split` = `test`);
  the other 55 are `train.jsonl`. The harness rules are written against the benchmark and never see the held-out ones.
- Train, held-out and bench share no exercise (tested). The held-out set is for the model's accuracy and calibration, the bench set for the
  same-benchmark comparison of step 5.

## Regenerate

```
python decision/make_exercises.py     # only to rebuild decision/exercises/ (needs caladrius-mcp, see apothicaire.MCP_BIN); byte-identical for the same engine
python decision/make_dataset.py       # recreates decision/data/train.jsonl, heldout.jsonl and bench.jsonl and the counts block below; about 10 s, no engine needed
python -m unittest discover -s tests -t .     # whole suite (about 45 s); only this file: python -m unittest tests.test_decision_dataset
```

The tests are `unittest`-based like the others (pytest is not installed here, but collects them). `decision/data/` is git-ignored (22 MB,
deterministic: regeneration is byte-identical); the exercises are versioned.

## Step 2: zero-shot baseline

Liquid AI `d1-omni-600M` and `d1-3B` (license lfm1.0), no training, asked the 7 questions of that time (`parameter_asked` was then one `choice`, replaced by the 14 `asked_<key>` questions on 2026-10-09, step 4b) of every row in one `system_one(state, questions)` call
(`decision/zero_shot_d1.py`; environment in `decision/requirements-d1.txt`: torch 2.14.1+cu130, transformers 5.19.0). Full report with the
confusion of `analysis` and `parameter_asked`, the calibration tables and the times: [`runs/2026-10-09/report.md`](runs/2026-10-09/report.md)
(run folder: [`runs/2026-10-09/`](runs/2026-10-09/)). Accuracy over all questions of the rows (one-hot gold):

| model | split | rows | overall | ECE | ms per row |
|---|---|---|---|---|---|
| d1-omni-600M (cuda, float16) | held-out | 720 (all) | 61.8 % | 0.084 | 134 |
| d1-omni-600M (cuda, float16) | bench | 900 (all) | 62.2 % | 0.076 | 140 |
| d1-omni-600M (cuda, float16) | held-out, every 6th row | 120 | 63.1 % | 0.083 | 136 |
| d1-3B (cpu, float32) | held-out, every 6th row | 120 | 66.3 % | 0.101 | 14160 |
| d1-omni-600M (cuda, float16) | bench, every 8th row | 112 | 65.2 % | 0.087 | 136 |
| d1-3B (cpu, float32) | bench, every 8th row | 112 | 66.8 % | 0.090 | 14180 |

Per question (held-out rows every 6th, 600M / 3B): `analysis` 68.3 / 90.0 %, `parameter_asked` 51.7 / 86.7 %, `route` 68.3 / 74.2 %,
`auc_method` 60.8 / 75.8 %, `dose_has_unit` 75.8 / 87.5 %, `is_not_available` 70.8 / 28.3 %, `compare_pair` 45.8 / 21.7 %.

- **d1-3B does not run on the RTX 3060 here.** The weights fit (6.8 GB used of 12 after load) but the model's remote code calls
  `torch.ops.aten._flash_attention_forward`, which the PyTorch Windows wheel was not built with (`USE_FLASH_ATTENTION was not enabled for build`).
  Nothing was patched; the 3B was run on CPU in float32 on a strided subset (about 14 s per row, so 120 and 112 rows). Details in the report notes.
- Two questions are below the always-answer-the-majority baseline on both models: `is_not_available` (92 % false) and `compare_pair`
  (92 % `not_applicable`); the 3B is at 28 % and 22 % there: it answers `true` on 86 of the 107 rows that are false (and finds all 13 true ones), and gives a pair or `none_available` on 94 of 112 rows that compare nothing. `auc_method` is below the majority
  baseline too. The models are better than the baseline only on `analysis`, `parameter_asked`, `route` and `dose_has_unit`.
- Calibration: the 600M is under-confident at low probability (bins below 0.5 are right about 50 % of the time) and well calibrated
  above 0.7; ECE about 0.08. The 3B is overconfident on the two rare-class questions.
- The 3B is better than the 600M on the same rows except on the two rare-class questions, with the largest gain on `analysis` (+22 points)
  and `parameter_asked` (+35 points). This is what fine-tuning (step 3) has to fix: rare classes and calibration.

## Counts (class balance)

<!-- counts:begin -->

| file | rows | exercises |
|---|---|---|
| train.jsonl | 1980 | 55 |
| heldout.jsonl | 720 | 20 |
| bench.jsonl | 900 | 25 |

`analysis`

| answer | train | heldout | bench |
|---|---|---|---|
| compare | 165 | 60 | 75 |
| fit_pk1 | 165 | 60 | 75 |
| fit_pk2 | 165 | 60 | 75 |
| nca | 165 | 60 | 75 |
| none_needed | 1155 | 420 | 525 |
| simulate | 165 | 60 | 75 |

`route`

| answer | train | heldout | bench |
|---|---|---|---|
| iv_bolus | 520 | 231 | 241 |
| iv_infusion | 180 | 89 | 95 |
| oral | 968 | 314 | 448 |
| unknown | 312 | 86 | 116 |

`auc_method`

| answer | train | heldout | bench |
|---|---|---|---|
| lin_up_log_down | 165 | 60 | 75 |
| linear | 165 | 60 | 75 |
| not_applicable | 1650 | 600 | 750 |

`asked_cmax`

| answer | train | heldout | bench |
|---|---|---|---|
| false | 1672 | 605 | 757 |
| true | 308 | 115 | 143 |

`asked_tmax`

| answer | train | heldout | bench |
|---|---|---|---|
| false | 1679 | 608 | 760 |
| true | 301 | 112 | 140 |

`asked_c0`

| answer | train | heldout | bench |
|---|---|---|---|
| false | 1844 | 674 | 836 |
| true | 136 | 46 | 64 |

`asked_auclast`

| answer | train | heldout | bench |
|---|---|---|---|
| false | 1621 | 587 | 736 |
| true | 359 | 133 | 164 |

`asked_aucinf`

| answer | train | heldout | bench |
|---|---|---|---|
| false | 1743 | 637 | 788 |
| true | 237 | 83 | 112 |

`asked_lambda_z`

| answer | train | heldout | bench |
|---|---|---|---|
| false | 1782 | 648 | 812 |
| true | 198 | 72 | 88 |

`asked_half_life`

| answer | train | heldout | bench |
|---|---|---|---|
| false | 1669 | 609 | 759 |
| true | 311 | 111 | 141 |

`asked_cl`

| answer | train | heldout | bench |
|---|---|---|---|
| false | 1671 | 608 | 760 |
| true | 309 | 112 | 140 |

`asked_vz`

| answer | train | heldout | bench |
|---|---|---|---|
| false | 1673 | 613 | 763 |
| true | 307 | 107 | 137 |

`asked_mrt`

| answer | train | heldout | bench |
|---|---|---|---|
| false | 1751 | 636 | 798 |
| true | 229 | 84 | 102 |

`asked_aucpext`

| answer | train | heldout | bench |
|---|---|---|---|
| false | 1861 | 676 | 848 |
| true | 119 | 44 | 52 |

`asked_lambda_z_points`

| answer | train | heldout | bench |
|---|---|---|---|
| false | 1839 | 669 | 837 |
| true | 141 | 51 | 63 |

`asked_adj_r2`

| answer | train | heldout | bench |
|---|---|---|---|
| false | 1862 | 676 | 844 |
| true | 118 | 44 | 56 |

`asked_tlag`

| answer | train | heldout | bench |
|---|---|---|---|
| false | 1913 | 692 | 872 |
| true | 67 | 28 | 28 |

`dose_has_unit`

| answer | train | heldout | bench |
|---|---|---|---|
| false | 323 | 131 | 144 |
| true | 1657 | 589 | 756 |

`is_not_available`

| answer | train | heldout | bench |
|---|---|---|---|
| false | 1815 | 660 | 825 |
| true | 165 | 60 | 75 |

`compare_pair`

| answer | train | heldout | bench |
|---|---|---|---|
| 2+3 | 165 | 60 | 75 |
| not_applicable | 1815 | 660 | 825 |

<!-- counts:end -->

## Limits

- The turns are the scripted ones of the benchmark plus 4 extra kinds: the questions are templates, the dataset teaches the model the
  intent behind a fixed set of sentences, not free French. The paraphrases (4 to 5 per kind, 5 introductions) are written by hand, no
  model; they vary the wording, not the register or the typos of real students.
- `none_needed` is 58 % of the `analysis` answers (1155 of 1980 train rows): not rebalanced here. If the model over-predicts it, step 3
  can weight or subsample these rows.
- Class balance is poor by construction: `is_not_available` is true on 1 row out of 12, `compare_pair` is `not_applicable` on 11 out of 12.
  Each `asked_<key>` is false on most rows (true on 3 % of the train rows for `asked_tlag`, 6 to 7 % for `asked_adj_r2`, `asked_aucpext`, `asked_c0` and `asked_lambda_z_points`, 10 to 18 % for the others).
  Rows by number of true `asked_*` (train / held-out / bench): 0 true 660 / 240 / 300, 1 true 687 / 251 / 309, 2 true 436 / 156 / 202,
  3 true 32 / 13 / 14, 9 true 165 / 60 / 75 (the first request).
- Labels are decided by the generator, not by annotators: one-hot gold, so calibration on this set measures the model against a
  certain truth, not against annotator disagreement; ambiguous requests (a user who gives no AUC method, no unit and no route) are not covered.
- `route` = `unknown` and `dose_has_unit` = false come from synthetic omissions in the sentence, not from the exercise data.
- Exercises are single-subject, one dose, simulated one- and two-compartment models with proportional noise; no multi-subject files,
  no wrong-unit CSV headers, no data error.

## Step 4: harness with gold decisions (upper bound)

`decision/harness.py` is the deterministic part of the decision path. It holds one Caladrius MCP session, using the client of `apothicaire.py`.
On each turn it builds the state with `make_dataset.make_state` and `split_first_message`, the same code that writes the dataset rows. It asks
`decide(state, questions)` for answers and then acts on them: `data_import` once, `nca_run` with the decided route and AUC method,
`analysis_get` for the parameter asked, `analysis_compare` on the decided pair, or a stated refusal. Finally it renders French templates. The only
numbers in an answer are engine values, shown as in the digests of `apothicaire.py`. No language model is used and no arithmetic is done on engine
values. When the route, the dose, the dose unit or the infusion duration is missing, the template asks for it. A duration in a time unit other
than the data's is asked for again in the data's unit. `decision/run_harness.py` runs the 25 benchmark exercises with the 8 scripted turns. It
writes the per-exercise JSON and `report.md` of `bench/run_bench.py`, scored by the unchanged `bench/score.py`:

```
python decision/run_harness.py --decider gold          # answers = gold labels of data/bench.jsonl; or --decider module:function
python -m unittest tests.test_decision_harness         # templates (golden strings), action mapping, refusals, state, real engine
```

Gold run (`runs/2026-10-09-harness-gold/report.md`), next to the 27B pipeline on the same exercises (`bench/runs/2026-10-09b`):

| pipeline | oracle-correct turns | oracle-correct numbers | invalid or failed tool calls | gate: unverified numbers | time per turn |
|---|---|---|---|---|---|
| 27B + gate (2026-10-09b) | 170 / 175 | 549 / 556 | 0 / 160 | 0 / 926 | 10.4 s |
| decision harness, gold decisions | **175 / 175** | **558 / 558** | **0 / 250** | 0 / 1698 | 1.4 ms (no model) |

- 558 against 556 numbers: the compare turn also expects the engine's difference and percentage when `analysis_compare` was usable. That was
  the case for 25 of 25 turns here and 24 of 25 for the 27B.
- The time covers the engine calls and the rendering only. Add about 1.1 s per exercise for the MCP start and the scorer's chance baseline,
  plus the decision model's own latency in steps 2 and 3. There are no prompt tokens and no VRAM.
- The scorer and the oracle agree on every turn (0 disagreements). The tool-argument audit finds 0 deviating calls in 75. Over the 200 turns
  the harness made 225 decide calls, because the compare turn is decided again after its re-run (see below). There were no harness notes:
  `is_not_available` was never overruled by the engine.

**Failures, one by one.** The first pass scored 171 / 175 turns and 550 / 558 numbers. All 4 failing turns and 8 numbers had one cause, of
class **template**: AUC values above one million were printed as the digest gives them, e.g. "1701680.0". The digest rounds to 6
significant digits and Python adds ".0", so the number claims 8 digits, and the oracle rightly rejected it (`missing_value`). The cases:
ex18_pk2_iv_bolus t1 (AUC(0-tlast), AUC(0-inf)), ex18 t7 (both AUC(0-tlast)), ex23_iv_bolus t1 (AUC(0-tlast), AUC(0-inf)) and ex23 t7 (both
AUC(0-tlast)). The fix is in `value_text`, which drops the trailing ".0" of an integral float. This is a display change and the digits are
never altered; a test covers it. The rerun above has no failure, so the counts are engine option 0, scorer label 0, other 0. The ceiling is
above the 27B's 170. Its 5 failures do not occur here: the recall writes the dose unit taken from the user's sentence (3 `missing_unit` for
the 27B), and the compare turn always calls `analysis_compare` and labels both AUC (2 `missing_value` for the 27B).

What this ceiling does not measure:
- **(closed in step 4b)** `parameter_asked` = `several` used to let the harness answer with the table of 13 parameters; see Step 4b.
- **The gold decider is not a model.** It finds the scripted row by the state without its analyses: the dataset draws some reading turns
  "late", and it describes the compare turn after the re-run. On the first ask of every compare turn its `compare_pair` ("2+3") is outside
  the offered options (25 / 25). This is expected and the harness does not use it: the pair is decided on the state after the re-run
  (open, see Step 4b).
- **The style of the answers follows the engine.** Numbers keep the engine's decimal point. Engine messages (reasons, unit warnings) are
  quoted in English. The dose unit is never sent to Caladrius, as in the 27B pipeline, so CL and V are in "dose unit/(...)"; the recall
  says so.
- **What is not covered.** `fit_pk1`, `fit_pk2` and `simulate` are not wired; the template says so, and the benchmark never asks for them.
  The dose, the infusion duration and the column units are read from the user's text with fixed patterns, and anything outside them is
  asked for.

## Step 4b: an honest ceiling (one `asked_<key>` question per parameter)

`parameter_asked` is gone. The question set has 14 `noul` questions `asked_cmax`, `asked_tmax`, ..., `asked_tlag` (same keys as the old options, without
`several` and `none`), gold true when the turn names the parameter (table in "Our rows"; datasets regenerated: same 1980 / 720 / 900 rows, 20 questions
per row instead of 7). The harness acts on them: `analysis_get` and the NCA template print only the parameters answered true, in the engine's
order (the order of the engine's `parameters`, not the order of the questions); a parameter Caladrius did not compute is still said with the engine's
reason. An NCA turn where no `asked_*` is true runs the analysis, prints no value and says that no parameter was designated (`T_NO_PARAMETER`); a
reading turn where none is true is the recall of the settings. `analysis_compare` is called with the parameters asked. The `import_nca` wording
"tous les paramètres standards" was rewritten to name the nine parameters, so no wording asks for something that is not in the gold.

Gold run on the 25 benchmark exercises (`python decision/run_harness.py --decider gold`, folder
[`runs/2026-10-09-harness-gold-asked/`](runs/2026-10-09-harness-gold-asked/report.md), scored by the unchanged `bench/score.py`):

| pipeline | oracle-correct turns | oracle-correct numbers | invalid or failed tool calls | gate: unverified numbers | time per turn |
|---|---|---|---|---|---|
| decision harness, gold, `parameter_asked` (step 4) | 175 / 175 | 558 / 558 | 0 / 250 | 0 / 1698 | 1.4 ms |
| decision harness, gold, `asked_<key>` (step 4b) | **175 / 175** | **558 / 558** | **0 / 250** | 0 / 691 | 1 ms |

- The ceiling holds at 175 / 175 turns and 558 / 558 numbers, now with exactly the parameters asked: the numbers written in the answers go from
  1698 to 691 (the old table of 13 parameters is no longer printed; the gate counts every number of an answer). No failure to list: the
  scorer and the oracle agree on every turn (0 disagreements), 0 deviating tool calls, no harness note, so the failure counts by class are
  all 0 (engine option 0, scorer label 0, template 0, other 0). The first ceiling was therefore not inflated in oracle terms; it was only
  not exact. What a model must now get right is 14 booleans per turn instead of one choice, and a missed `asked_*` removes a number that
  the oracle then counts as `missing_value`, where before the table covered it.
- **Item (b), the compare turn asked twice, is not fixed.** Gold `compare_pair` before the re-run would have to name an analysis that
  does not exist yet ("2+3" with 3 not run), so the question set needs a new option (for example `<id>+new`: compare with the analysis the
  harness runs for this request) and the compare rows have to be described before the re-run. That changes the answer set of every state with
  at least one analysis, so it is left for the step 3 / 5 design. The harness still asks twice on the compare turn (225 decide calls in 200
  turns); the first ask's `compare_pair` is outside the options (25 / 25), unused.
