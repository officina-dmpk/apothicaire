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
| `analysis` | choice | nca, fit_pk1, fit_pk2, simulate, compare, none_needed, not_supported | turn kind: `import_nca`, `nca_oneline` -> nca; `compare`, `compare_directed` -> compare; fit / simulate kinds; `not_supported` (out-of-scope asks: bioequivalence, population PK, steady state, urine, an explanation, a plot, a parameter outside the 14) -> not_supported; every question about a result already computed (and the recall, and the not-available question) -> none_needed |
| `route` | choice | iv_bolus, iv_infusion, oral, unknown | `meta.json` route when the user's text gives one (a route phrase of the introduction, a `{route}` slot, or a route the one-line wording implies and declares: "comprimé", "perfusé sur 1 h", "injecté en bolus"); `unknown` when the text is silent (introduction drawn without its route phrase, or a one-line wording declared `route: none`) |
| `auc_method` | choice | linear, lin_up_log_down, not_applicable | the NCA kinds take the method their wording declares (linear when it names none: the method the analysis needs to run; scripted: linear); the compare turn re-runs with lin_up_log_down; every other kind, the directed compare of two existing analyses included, runs no NCA: not_applicable |
| `asked_<key>` (14 questions: `asked_cmax`, `asked_tmax`, `asked_c0`, `asked_auclast`, `asked_aucinf`, `asked_lambda_z`, `asked_half_life`, `asked_cl`, `asked_vz`, `asked_mrt`, `asked_aucpext`, `asked_lambda_z_points`, `asked_adj_r2`, `asked_tlag`) | noul | false, true | true for the parameters the wording declares in `asked` (`wordings.json`; the scripted wording: the benchmark's). A negated parameter ("pas l'AUC, seulement la demi-vie") or a corrected one ("la Cmax… non, le Tmax") is not asked. All false on a recall, a fit, a simulation and an out-of-scope request. The not-available turn asks at least one parameter Caladrius does not compute for the route (C0 after an oral dose or an infusion, Tlag after an IV dose), possibly with a computed one; no other turn asks one |
| `dose_has_unit` | noul | false, true | the generator's draw of how the dose is written: with the exercise's unit or in another unit ("0,4 g" for 400 mg, "2 mg" for 2000 µg) -> true; the number alone, or no dose at all (a one-line wording declared `dose: none`) -> false |
| `is_not_available` | noul | false, true | true exactly for the `not_available` kind: a parameter asked is in `ground_truth.nca.linear.not_calculated` of `meta.json` |
| `compare_pair` | choice | `not_applicable` and one key `a+b` per ordered pair of analysis ids present (`2+3` and `3+2`: a is the reference, b - a); `none_available` when fewer than two analyses exist | the re-run compare turn: `2+3` (the linear analysis is the reference); the directed compare: `ref+other`, the reference the wording names (named first, or named as the reference against a negated or corrected other one), drawn 2 or 3 per row |

No label is computed from a pattern over the text: they come from `meta.json`, the turn kind, the declared intent of the wording and the
generator's draws (tested: the rows where a pattern would fail, an implied route or a dose in g, are labelled from the intent).

Turn kinds (15): the 8 scripted ones of `bench/scripts.py` (import_nca, cmax_tmax, clearance_volume, half_life, lambda_z_regression, recall,
compare, not_available) and 7 extra kinds: `nca_other` (AUC, MRT, lambda_z read from the NCA already run), `fit_pk1`, `fit_pk2`, `simulate`,
`nca_oneline` (a first message on one line: the request carries the dose, in its unit, in another unit, without a unit, said wrongly then
corrected, or absent, and the route, named, implied or absent), `compare_directed` (two existing analyses compared, the reference named),
`not_supported` (out-of-scope).

## Wordings (`decision/wordings.json`)

Every French sentence the generator writes is in `decision/wordings.json` (data only, read by `make_dataset.py`): 15 request pools
(one per turn kind, 12 to 19 wordings each) and 5 slot pools (introductions of the data, route phrases per route, BLQ notes). Each wording
has an id (`<kind>.<nn>`), one family tag and its declared intent (`asked`; `auc_method` for the NCA kinds; `oneline`, `dose`, `route` for a
one-line first message). Families: formal, colloquial, abbreviated (t1/2, AUC0-t, AUC0-inf, Cl/F, Vd, λz), implicit-route, unit-in-text,
multi-parameter, negation, correction-in-sentence, out-of-scope, directed-compare, follow-up, no-dose, no-route, method-stated. The scripted
wording of the benchmark (`bench/scripts.py`) is not in the file and is always on the train side.

The reviewer's 74 requests (`ood/requests.jsonl`) were not copied nor paraphrased: they stay a frozen test set. A test checks that no wording
and no sentence of any generated row equals one of them after normalisation (lower case, no accents, numbers as 0) or shares more than
60 % of its word trigrams (Jaccard); the highest similarity is 0.24.

Per (exercise, kind): the scripted wording (scripted kinds) and 2 paraphrases (3 for the extra kinds, 4 for `nca_oneline`), distinct,
drawn among the wordings of the pool that fit the exercise (a wording that implies a route only on exercises of that route; C0 or Tlag
only where Caladrius computes them, except on the not-available turn). A turn that is not a one-line first message has an introduction
line; the dose is written with its unit (60 %), in another unit (20 %) or without a unit (20 %); 20 % of the introductions drop the route
phrase (not on `not_available` rows, where the route decides the answer). 30 % of the not-available (one parameter), out-of-scope and fit
rows are the first message (no analysis yet). Conventions of the state: the compare turns are described with analyses 2 (linear) and 3
(lin-up/log-down) present, the re-run one after its re-run; in 40 % of the rows of the reading kinds, the fits and the out-of-scope asks
both analyses are present (the question comes later in the conversation); a `simulate` state holds a fit as analysis 3.

<!-- wordings:begin -->

Wording split: seed 20261011, attempt 5.

| pool | wordings | train side | held out |
|---|---|---|---|
| import_nca | 16 | 12 | 4 |
| cmax_tmax | 14 | 10 | 4 |
| clearance_volume | 13 | 10 | 3 |
| half_life | 13 | 10 | 3 |
| lambda_z_regression | 12 | 9 | 3 |
| recall | 13 | 10 | 3 |
| compare | 13 | 10 | 3 |
| not_available | 15 | 11 | 4 |
| nca_other | 13 | 10 | 3 |
| fit_pk1 | 13 | 10 | 3 |
| fit_pk2 | 13 | 10 | 3 |
| simulate | 12 | 9 | 3 |
| nca_oneline | 19 | 14 | 5 |
| compare_directed | 14 | 10 | 4 |
| not_supported | 17 | 13 | 4 |
| intro | 13 | 10 | 3 |
| route_oral | 6 | 4 | 2 |
| route_iv_bolus | 6 | 4 | 2 |
| route_iv_infusion | 6 | 4 | 2 |
| blq_note | 5 | 4 | 1 |
| all | 246 | 184 | 62 |

| family | wordings | train side | held out | pools |
|---|---|---|---|---|
| formal | 48 | 32 | 16 | import_nca, cmax_tmax, clearance_volume, half_life, lambda_z_regression, recall, compare, not_available, nca_other, fit_pk1, fit_pk2, simulate, nca_oneline, compare_directed, intro, route_oral, route_iv_bolus, route_iv_infusion, blq_note |
| colloquial | 36 | 29 | 7 | import_nca, cmax_tmax, clearance_volume, half_life, lambda_z_regression, recall, compare, not_available, nca_other, fit_pk1, fit_pk2, simulate, nca_oneline, compare_directed, not_supported, intro, route_oral, route_iv_bolus, route_iv_infusion, blq_note |
| abbreviated | 41 | 33 | 8 | import_nca, cmax_tmax, clearance_volume, half_life, lambda_z_regression, recall, compare, not_available, nca_other, fit_pk1, fit_pk2, simulate, nca_oneline, compare_directed, not_supported, intro, route_oral, route_iv_bolus, route_iv_infusion, blq_note |
| implicit-route | 11 | 7 | 4 | fit_pk1, fit_pk2, nca_oneline, route_oral, route_iv_bolus, route_iv_infusion |
| unit-in-text | 5 | 4 | 1 | fit_pk1, fit_pk2, nca_oneline, intro |
| multi-parameter | 16 | 10 | 6 | import_nca, cmax_tmax, clearance_volume, half_life, lambda_z_regression, compare, not_available, nca_other, nca_oneline |
| negation | 21 | 18 | 3 | import_nca, cmax_tmax, clearance_volume, half_life, lambda_z_regression, recall, compare, not_available, nca_other, fit_pk1, fit_pk2, simulate, nca_oneline, compare_directed, not_supported |
| correction-in-sentence | 18 | 16 | 2 | import_nca, cmax_tmax, clearance_volume, half_life, lambda_z_regression, recall, compare, not_available, nca_other, fit_pk1, fit_pk2, simulate, nca_oneline, compare_directed, not_supported |
| out-of-scope | 11 | 8 | 3 | not_supported |
| directed-compare | 7 | 3 | 4 | compare_directed |
| follow-up | 20 | 15 | 5 | cmax_tmax, clearance_volume, half_life, lambda_z_regression, recall, compare, not_available, nca_other, fit_pk1, fit_pk2, simulate, not_supported |
| no-dose | 5 | 4 | 1 | fit_pk1, fit_pk2, nca_oneline, not_supported |
| no-route | 2 | 1 | 1 | nca_oneline |
| method-stated | 5 | 4 | 1 | import_nca, compare, nca_oneline |

Held-out wording ids: blq_note.04, clearance_volume.06, clearance_volume.10, clearance_volume.13, cmax_tmax.03, cmax_tmax.07, cmax_tmax.08, cmax_tmax.10, compare.04, compare.12, compare.13, compare_directed.01, compare_directed.04, compare_directed.10, compare_directed.12, fit_pk1.02, fit_pk1.07, fit_pk1.10, fit_pk2.08, fit_pk2.09, fit_pk2.12, half_life.02, half_life.03, half_life.08, import_nca.01, import_nca.07, import_nca.12, import_nca.14, intro.03, intro.11, intro.13, lambda_z_regression.01, lambda_z_regression.02, lambda_z_regression.09, nca_oneline.02, nca_oneline.07, nca_oneline.08, nca_oneline.12, nca_oneline.15, nca_other.08, nca_other.10, nca_other.13, not_available.04, not_available.08, not_available.09, not_available.10, not_supported.04, not_supported.06, not_supported.09, not_supported.14, recall.04, recall.09, recall.11, route_iv_bolus.01, route_iv_bolus.04, route_iv_infusion.03, route_iv_infusion.04, route_oral.04, route_oral.05, simulate.06, simulate.09, simulate.12.

<!-- wordings:end -->

## Exercises and splits

- `bench/exercises/`: the 25 benchmark exercises (read only here). All of them go to `bench.jsonl` (`split` = `bench`, ids `be_...`,
  `factors.bench = true`, train-side wordings). That file is never used for training or calibration: it is the comparison set against the
  27B pipeline (step 5).
- `decision/exercises/`: 75 more, 3 seeds (31415926, 27182818, 16180339) of the same plan, generated by `decision/make_exercises.py`
  with `bench/make_exercises.py` (the benchmark seed is 20261009; a draw the oracle rejects is redrawn, see `meta.json` `attempt`).
- **By exercise**: 20 whole exercises drawn with seed 20261010 among the 75 new ones are held out; the other 55 are train exercises.
- **By wording** (v2): in every pool of `wordings.json`, round(25 %) of the wordings (at least one) drawn with seed 20261011 are held out
  and never appear in a row of `train.jsonl`, `heldout_exercises.jsonl` or `bench.jsonl`; the draw is redrawn until every family has
  wordings on both sides, every parameter is asked by a wording on both sides, and every kind keeps, for every route, enough train-side
  wordings and at least one held-out one (attempt number in the block above). The held-out-wording rows take their introduction, route
  phrase and BLQ note from the held-out side too.
- Files (`split` = `test` and ids `te_...` unique over the three held-out files; `factors.file` names the file):

  | file | exercises | wordings | rows per exercise |
  |---|---|---|---|
  | `train.jsonl` | 55 train | train side + scripted | 46 (8 scripted + 38 paraphrases) |
  | `heldout_exercises.jsonl` | 20 held out | train side + scripted | 46 |
  | `heldout_wordings.jsonl` | 55 train | held out | 15 (one per kind) |
  | `heldout_both.jsonl` | 20 held out | held out | up to 30 (two per kind when two held-out wordings fit) |
  | `bench.jsonl` | the 25 of the benchmark | train side + scripted | 46 |

  `heldout_exercises` measures new exercises in known wordings (the v1 measure, 99.9 % in v1), `heldout_wordings` known exercises in
  unseen wordings, `heldout_both` both unseen. Tested: no held-out wording id (request, introduction, route phrase, BLQ note) in a
  train-side row and no held-out request sentence in train; no exercise shared between train / held-out / bench; every `analysis` option
  (with `not_supported`), every `route`, `auc_method`, both pair directions and every `asked_*` true in train and in each held-out file.
- The previous `heldout.jsonl` (v1) is no longer written; a copy left in `decision/data/` is stale (the Bonsai baseline of 2026-10-10
  reads it).

## Regenerate

```
python decision/make_exercises.py     # only to rebuild decision/exercises/ (needs caladrius-mcp, see apothicaire.MCP_BIN); byte-identical for the same engine
python decision/make_dataset.py       # recreates the five files of decision/data/ and the two generated blocks of this README; about 3 s, no engine needed
python -m unittest discover -s tests -t .     # whole suite; only this file: python -m unittest tests.test_decision_dataset
```

The tests are `unittest`-based like the others (pytest is not installed here, but collects them). `decision/data/` is git-ignored
(deterministic: regeneration is byte-identical); the exercises and `wordings.json` are versioned.

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

v1 (2026-10-09), for the record: three files, split by exercise only, 83 distinct request sentences (4 to 5 hand-written paraphrases per
kind plus the scripted ones), every held-out request also a train request: `train.jsonl` 1980 rows / 55 exercises, `heldout.jsonl` 720 / 20,
`bench.jsonl` 900 / 25; `analysis` in train: none_needed 1155, nca, compare, fit_pk1, fit_pk2, simulate 165 each, no `not_supported` and no
`3+2` row. The trained 0.8B scored 99.9 % on that held-out file and 4 / 74 whole requests right on the reviewer's set (Step 6).

v2 (2026-10-10), generated:

<!-- counts:begin -->

| file | rows | exercises | request wordings (scripted ones counted once per kind) |
|---|---|---|---|
| train.jsonl | 2530 | 55 | 166 |
| heldout_exercises.jsonl | 920 | 20 | 164 |
| heldout_wordings.jsonl | 825 | 55 | 52 |
| heldout_both.jsonl | 593 | 20 | 52 |
| bench.jsonl | 1150 | 25 | 165 |

`analysis`

| answer | train | heldout_exercises | heldout_wordings | heldout_both | bench |
|---|---|---|---|---|---|
| compare | 330 | 120 | 110 | 80 | 150 |
| fit_pk1 | 165 | 60 | 55 | 40 | 75 |
| fit_pk2 | 165 | 60 | 55 | 40 | 75 |
| nca | 385 | 140 | 110 | 80 | 175 |
| none_needed | 1155 | 420 | 385 | 273 | 525 |
| not_supported | 165 | 60 | 55 | 40 | 75 |
| simulate | 165 | 60 | 55 | 40 | 75 |

`route`

| answer | train | heldout_exercises | heldout_wordings | heldout_both | bench |
|---|---|---|---|---|---|
| iv_bolus | 670 | 285 | 214 | 157 | 313 |
| iv_infusion | 234 | 118 | 76 | 71 | 117 |
| oral | 1261 | 408 | 406 | 246 | 547 |
| unknown | 365 | 109 | 129 | 119 | 173 |

`auc_method`

| answer | train | heldout_exercises | heldout_wordings | heldout_both | bench |
|---|---|---|---|---|---|
| lin_up_log_down | 204 | 75 | 55 | 40 | 94 |
| linear | 346 | 125 | 110 | 80 | 156 |
| not_applicable | 1980 | 720 | 660 | 473 | 900 |

`asked_cmax`

| answer | train | heldout_exercises | heldout_wordings | heldout_both | bench |
|---|---|---|---|---|---|
| false | 2210 | 799 | 696 | 508 | 996 |
| true | 320 | 121 | 129 | 85 | 154 |

`asked_tmax`

| answer | train | heldout_exercises | heldout_wordings | heldout_both | bench |
|---|---|---|---|---|---|
| false | 2201 | 806 | 752 | 546 | 1012 |
| true | 329 | 114 | 73 | 47 | 138 |

`asked_c0`

| answer | train | heldout_exercises | heldout_wordings | heldout_both | bench |
|---|---|---|---|---|---|
| false | 2398 | 876 | 789 | 566 | 1092 |
| true | 132 | 44 | 36 | 27 | 58 |

`asked_auclast`

| answer | train | heldout_exercises | heldout_wordings | heldout_both | bench |
|---|---|---|---|---|---|
| false | 2076 | 756 | 698 | 514 | 945 |
| true | 454 | 164 | 127 | 79 | 205 |

`asked_aucinf`

| answer | train | heldout_exercises | heldout_wordings | heldout_both | bench |
|---|---|---|---|---|---|
| false | 2273 | 840 | 730 | 536 | 1035 |
| true | 257 | 80 | 95 | 57 | 115 |

`asked_lambda_z`

| answer | train | heldout_exercises | heldout_wordings | heldout_both | bench |
|---|---|---|---|---|---|
| false | 2314 | 847 | 785 | 559 | 1064 |
| true | 216 | 73 | 40 | 34 | 86 |

`asked_half_life`

| answer | train | heldout_exercises | heldout_wordings | heldout_both | bench |
|---|---|---|---|---|---|
| false | 2200 | 805 | 682 | 487 | 1002 |
| true | 330 | 115 | 143 | 106 | 148 |

`asked_cl`

| answer | train | heldout_exercises | heldout_wordings | heldout_both | bench |
|---|---|---|---|---|---|
| false | 2245 | 831 | 766 | 552 | 1021 |
| true | 285 | 89 | 59 | 41 | 129 |

`asked_vz`

| answer | train | heldout_exercises | heldout_wordings | heldout_both | bench |
|---|---|---|---|---|---|
| false | 2250 | 819 | 751 | 548 | 1030 |
| true | 280 | 101 | 74 | 45 | 120 |

`asked_mrt`

| answer | train | heldout_exercises | heldout_wordings | heldout_both | bench |
|---|---|---|---|---|---|
| false | 2336 | 850 | 734 | 532 | 1058 |
| true | 194 | 70 | 91 | 61 | 92 |

`asked_aucpext`

| answer | train | heldout_exercises | heldout_wordings | heldout_both | bench |
|---|---|---|---|---|---|
| false | 2385 | 866 | 794 | 571 | 1085 |
| true | 145 | 54 | 31 | 22 | 65 |

`asked_lambda_z_points`

| answer | train | heldout_exercises | heldout_wordings | heldout_both | bench |
|---|---|---|---|---|---|
| false | 2409 | 878 | 784 | 557 | 1099 |
| true | 121 | 42 | 41 | 36 | 51 |

`asked_adj_r2`

| answer | train | heldout_exercises | heldout_wordings | heldout_both | bench |
|---|---|---|---|---|---|
| false | 2392 | 863 | 775 | 557 | 1086 |
| true | 138 | 57 | 50 | 36 | 64 |

`asked_tlag`

| answer | train | heldout_exercises | heldout_wordings | heldout_both | bench |
|---|---|---|---|---|---|
| false | 2455 | 886 | 805 | 584 | 1115 |
| true | 75 | 34 | 20 | 9 | 35 |

`dose_has_unit`

| answer | train | heldout_exercises | heldout_wordings | heldout_both | bench |
|---|---|---|---|---|---|
| false | 461 | 171 | 172 | 128 | 207 |
| true | 2069 | 749 | 653 | 465 | 943 |

`is_not_available`

| answer | train | heldout_exercises | heldout_wordings | heldout_both | bench |
|---|---|---|---|---|---|
| false | 2365 | 860 | 770 | 560 | 1075 |
| true | 165 | 60 | 55 | 33 | 75 |

`compare_pair`

| answer | train | heldout_exercises | heldout_wordings | heldout_both | bench |
|---|---|---|---|---|---|
| 2+3 | 238 | 89 | 79 | 55 | 113 |
| 3+2 | 92 | 31 | 31 | 25 | 37 |
| not_applicable | 2200 | 800 | 715 | 513 | 1000 |

<!-- counts:end -->

## Limits

- The requests are still templates written by one author: 210 request wordings and 36 slot wordings, filled with the exercise's values.
  The held-out wordings are new sentences, not new authors; the reviewer's 74 requests remain the test of another writer.
- `none_needed` is 46 % of the `analysis` answers of train (1155 of 2530): not rebalanced. `nca` is 15 % (385, 220 of them one-line
  first messages).
- Class balance is poor by construction: `is_not_available` is true on 1 row out of 15 (165 of 2530), `compare_pair` is `not_applicable`
  on 87 % of the train rows and `3+2` on 92. Each `asked_<key>` is false on most rows (true on 3 % of the train rows for `asked_tlag`, 5 to
  6 % for `asked_c0`, `asked_lambda_z_points`, `asked_adj_r2`, `asked_aucpext`, 8 to 18 % for the others). Rows by number of true
  `asked_*` in train: 0 true 863, 1 true 927, 2 true 485, 3 true 126, 4 true 32, 9 true 97.
- Labels are decided by the generator, not by annotators: one-hot gold, so calibration on this set measures the model against a
  certain truth, not against annotator disagreement. Conventions a reader may dispute: an NCA request that names no method is labelled
  `linear`; a directed compare of two existing analyses has `auc_method` = not_applicable (the reviewer's gold says lin_up_log_down on
  ood-015 and ood-072); "Cl/F" or "Vd/F" written after an IV dose is labelled `cl` / `vz`.
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


## Step 3: fine-tuning Qwen3.5-0.8B (Unsloth, native Windows)

`decision/train_unsloth.py` (recipe of the Unsloth decision-model page: `FastDecisionModel` 4-bit, LoRA r=16, `DecisionTrainer`, `calibrate`,
`save_pretrained` and `save_pretrained_merged`) trains on `train.jsonl` and evaluates and calibrates on `heldout.jsonl`; it reads the questions each row
declares. `decision/predict_unsloth.py` scores a saved model with the metric functions of `zero_shot_d1.py` (accuracy per question next to the
always-majority baseline, confusion tables, calibration). Environment: `requirements-unsloth.txt` (PyPI `unsloth==2026.10.3`, no WSL). Smoke run and
install problems: [`runs/2026-10-09-smoke-unsloth/report.md`](runs/2026-10-09-smoke-unsloth/report.md). Full run, 1980 rows, 2 epochs, `--max-seq-length 2560`
(0 inputs cut, the 2048 of the smoke run cut 2 to 6 %), 54 min of training, 3.6 GB torch peak:
[`runs/2026-10-09-train-qwen35-0.8b/report.md`](runs/2026-10-09-train-qwen35-0.8b/report.md).

| set | rows | questions right | always-majority | ECE | ms per row (cuda) |
|---|---|---|---|---|---|
| held-out | 720 | 14386 / 14400 = 99.9 % | 84.6 % | 0.0011 | 175 |
| bench | 900 | 17982 / 18000 = 99.9 % | 85.0 % | 0.0011 | 176 |

Every question is at 100.0 % except `is_not_available` (98.1 % held-out, 98.0 % bench, against 91.7 % for always answering `false`; recall of the `true`
class 78 % and 77 %). **No question is at or below its majority baseline.** The result is within the distribution of the generator: new exercises, but
the same hand-written wordings (see the report, and the limit stated at the end of Step 5).

## Step 5: the trained model drives the harness on the 25 benchmark exercises

`decision/decider_unsloth.py` is the decider: the merged model is loaded once on cuda, one `FastDecisionModel.predict` call answers the 20 questions of
the harness's state, a choice is its likeliest option, a `noul` is `true` when P(true) is at least 0.5. The confidence of each answer (and the seconds of the call) go into the
run JSON (`decisions[i].model_info`), and `decider_summary.json` has the calls and the GPU memory. `harness.py` and `run_harness.py` only gained that
pass-through (and the run folder name now keeps a dot).

```
python decision/run_harness.py --decider decider_unsloth:decide        # folder runs/2026-10-09-harness-qwen35-0.8b/, scored by the unchanged bench/score.py
```

| pipeline | oracle-correct turns | oracle-correct numbers | invalid or failed tool calls | gate: unverified numbers | time per turn | GPU memory |
|---|---|---|---|---|---|---|
| 27B + gate (2026-10-09b) | 170 / 175 | 549 / 556 | 0 / 160 | 0 / 926 | 10.4 s | not measured in this comparison |
| decision harness, gold decisions (step 4b) | 175 / 175 | 558 / 558 | 0 / 250 | 0 / 691 | 1 ms | none |
| decision harness, trained Qwen3.5-0.8B | **175 / 175** | **558 / 558** | **0 / 250** | 0 / 709 | 0.34 s (0.30 s without the first exercise's warm-up) | 1.9 GB torch peak, 2.9 GB `nvidia-smi` (0.7 GB of it other processes) |

- Folder: [`runs/2026-10-09-harness-qwen35-0.8b/`](runs/2026-10-09-harness-qwen35-0.8b/report.md). 225 decide calls in 200 turns (the compare turn asks twice,
  see Step 4b), 0.197 s per call (44.3 s in the model out of 88.8 s for the whole run), the rest is the engine and the scorer. The first exercise
  took 30 s instead of 2.4 s (CUDA kernel warm-up of the first calls); a warm server would not pay it.
- **No failing turn.** Oracle and scorer agree on every turn (0 disagreements), 0 deviating tool calls, 0 unverified numbers; the failure counts
  by class are all 0 (wrong decision 0, template 0, engine 0, scorer 0).
- **Where the model's decisions differ from the gold's (44 of 4500 answers), none changed a scored answer:**
  - 19 of the 25 `not_available` turns: `is_not_available` = `false` where the gold says `true` (confidence 0.54 to 0.85, the weakest answers of the
    run; the 6 other exercises are right). This is the known weak question (recall of the true class 78 %). The harness then takes its reading
    path: it calls `analysis_get` and the answer carries the engine's own statement "n'est pas calculé par Caladrius (« not defined for this route
    of administration »)" with a header line (analysis, method, dose, route) and the engine's unit warning in front, instead of the shorter refusal. The
    content is true and shows no value, but it is a different answer from the refusal template. The oracle does not cover the `not_available` kind
    (`not_covered`) and the scorer expects no number there, so both score it as correct: they cannot tell the two answers apart. The gate counts 709 numbers in the run against 691 for the gold run;
    the extra ones are in those headers (analysis id, dose), all engine values or user numbers, none unverified.
  - 25 of 25 compare turns: the first ask of `compare_pair` is `not_applicable`, which is within the offered options, where the gold is outside
    them (the pair does not exist before the re-run). Unused by the harness, which decides again after the re-run; both asks right.
- The model, when wrong, is unsure: all 19 wrong answers are below 0.86. A threshold (for example "below 0.9, ask or read the engine") would catch
  them, at the price of 26 of 4500 answers below 0.9; not implemented.
- **Limits of this comparison.** The 175 / 175 is on the benchmark exercises with the benchmark's wordings, which the model has not seen as exercises but
  whose sentence style is in its training distribution. It says that the decision pipeline works when the model answers right, which is the case on
  the held-out exercises too (99.9 %); it does not say how the model copes with a user who writes differently. The 27B pipeline was
  also tested on these wordings, but it reads free text. The next measure is a set of requests written by another person.
## Out-of-distribution requests (`decision/eval_ood.py`)

Requests written by an independent reviewer (`decision/ood/requests.jsonl`, format in `review-dsh-brief.md`) are converted to typed-decisions rows with the code
of this folder (`make_dataset.make_state`, `questions_for`; turn 1: the first line of `request` is the dose sentence, the last line the request; turn > 1:
the scripted first message of the exercise; prior analyses renumbered 2, 3 as the engine does), scored (per question with the always-majority baseline, per tag,
calibration, every wrong decision) and run through the harness (one fresh session per request, prior analyses replayed first). No oracle exists for free
requests: the report lists what a human must read and counts answers against refusals.

```
python decision/eval_ood.py --convert-only                      # rows.jsonl and schema_report.md (rejected lines and why)
python decision/eval_ood.py --decider gold                      # must give 100 %
python decision/eval_ood.py --decider majority
python decision/eval_ood.py --decider decider_unsloth:decide    # the trained model (GPU, .venv-unsloth)
```

Outputs: `decision/ood/runs/<date>-<decider>/{report.md, answers.jsonl, scores.json}`. Tests: `python -m unittest tests.test_eval_ood`.

## Step 6: the trained model on the reviewer's 74 requests

The measurement the project lacked: the trained Qwen3.5-0.8B (`models/qwen35-0.8b-d01/merged`, Step 3) run on the 74 hard French requests that an independent
reviewer (DeepSeek, blind) wrote with its own gold decisions (`ood/requests.jsonl`; its predictions are in `ood/REVIEW.md`, written before any run). Run of
2026-10-10 on the RTX 3060, `python decision/eval_ood.py --decider decider_unsloth:decide`; folder
[`ood/runs/2026-10-10-qwen35-0.8b/`](ood/runs/2026-10-10-qwen35-0.8b/report.md) (`report.md`, `answers.jsonl`, `scores.json`). Reference runs next to it:
`2026-10-10-gold` (the gold decisions), `2026-10-10-majority` (the label most frequent in train.jsonl) and `2026-10-10-rules-reviewer` (the reviewer's
deterministic rules of `ood/analyze_dataset.py`, wrapped by `ood/rules_decider.py`, applied to the same 74 rows).

Practical note: with the default Hugging Face cache, `import unsloth` did not return in 20 minutes of CPU time (the reviewer saw the same); pointing `HF_HOME`,
`HF_HUB_CACHE` and `HF_XET_CACHE` at a fresh folder makes it 18 s. The runs above were made that way.

**Conversion.** 74 of 74 lines converted. The first conversion accepted only 58: the 16 lines on the reviewer's 12 invented exercises were rejected with
`KeyError: 'nca'`. That was a defect of our converter, not of the requests: `bench/scripts.build_script` and the replay of prior analyses read the NCA oracle
(`ground_truth.nca`) of `meta.json`, which exercises written blind of the engine do not have, although the first message and the `nca_run` arguments need only
the route, the dose, the units and the table. Fixed with `bench/scripts.first_message` (the first message, now shared by `build_script`) and
`eval_ood.nca_arguments` (oracle arguments when present, else dose and route of `meta.json`; tested equal on the 25 benchmark exercises), with tests in
`tests/test_eval_ood.py`. `gold` gives 1480/1480 decisions and 74/74 requests all right. The converter warnings (ids renumbered 2, 3; three compare requests where
the analysis and the pair disagree; four refusals with an empty `asked`) are in `ood/schema_report.md`.

**Two scorers.** The tool scores the stored rows (questions in the sorted-key order of `train.jsonl`). The harness and the reviewer's own script
(`ood/eval_ood_model.py`, which runs with our model; output `ood/runs/eval_ood_model.json`) pass the questions in `questions_for` order, and the 0.8B model
answers 10 cells of 1480 differently (borderline cells). The reviewer's script gives 1335/1480 and 4/74 requests all right against our
1337/1480 and 4/74. Its second gold (`auc_method` replaced by the project convention: `not_applicable` unless the first NCA or a compare) gives `auc_method`
26/74, 1345/1480 and 8/74 requests all right. The verdict is the same under both golds; the tables below are the tool's.

### Per question

| question | trained model | reviewer's prediction | always-majority (these 74 rows) | majority learned on train.jsonl | reviewer's rules (these 74 rows) | reviewer's rules (held-out, in distribution) |
|---|---|---|---|---|---|---|
| `analysis` | **37.8 %** (28/74) | 82 % | 60.8 % | 21.6 % | 77.0 % | 95.3 % |
| `route` | **82.4 %** (61/74) | 90 % | 54.1 % | 54.1 % | 87.8 % | 100.0 % |
| `auc_method` | **21.6 %** (16/74) | 72 % | 77.0 % | 12.2 % | 74.3 % | 97.2 % |
| `dose_has_unit` | **98.6 %** (73/74) | 78 % | 93.2 % | 93.2 % | 100.0 % | 100.0 % |
| `is_not_available` | **85.1 %** (63/74) | 55 % | 85.1 % | 85.1 % | 91.9 % | 99.7 % |
| `compare_pair` | **100.0 %** (74/74) | 80 % | 94.6 % | 94.6 % | 100.0 % | 97.2 % |
| `asked_<parameter>` (mean of 14) | **98.6 %** | 88 % | 90.4 % | 90.4 % | 90.4 % (always false: the rules have no wording table) | not given |
| macro-average of the seven | **74.9 %** | ~80 % | 79.3 % | 64.5 % | 88.8 % | |
| all 20 questions, per decision | **90.3 %** (1337/1480) | | 86.6 % | 81.4 % | 89.9 % | 91.5 % |
| **all 20 questions right on a request** | **4/74 = 5.4 %** | 30 % | 0/74 | 0/74 | 1/74 | |

"Always-majority (these 74 rows)" is the best constant per question chosen with the gold of these rows (an upper bound for any constant); "majority learned on
train.jsonl" is the constant fit on the training data. The reviewer's rules were written from the generator's regexes; their held-out column is copied from
`ood/REVIEW.md` (in distribution), the other column is the same rules applied to these 74 rows (`asked_<parameter>` is always false for them).

The model is below the best constant on `analysis` (37.8 % against 60.8 %), on `auc_method` (21.6 % against 77.0 %) and on the macro-average (74.9 % against
79.3 %), and equal to it on `is_not_available`. Its 90.3 % per decision is above the constant (86.6 %) only because 14 of the 20 questions are mostly-false
`asked_<parameter>` booleans, which it gets right (98.6 %).

- `analysis`: the 45 requests whose gold is `nca` (all of them first requests) were all answered `none_needed`: the model never says `nca` on these 74 requests.
  It answers right the 8 compares, the 4 fits and 16 `none_needed` (11 of them first requests, right only because it says `none_needed` on every first request that
  it does not recognise). On the 12 follow-up turns: `analysis` 12/12, `route` 12/12, `is_not_available` 12/12, `auc_method` 3/12. On the 62 first requests:
  `analysis` 16/62, `route` 49/62, `auc_method` 13/62, `is_not_available` 51/62.
- `auc_method`: gold `linear` predicted `not_applicable` 56 times, `lin_up_log_down` predicted `not_applicable` twice: a consequence of the `analysis` collapse
  (in `train.jsonl` the method follows the action).
- `is_not_available`: 0 of the 11 true cases found (C0 after oral, Tlag after IV, Vss and ka, bioequivalence, population, steady state, urine); the model never
  answers `true`, so its score (85.1 %) is the constant.
- `route`: 7 of the 10 infusions ("Perfusion de ... sur/pendant ...", no word "intraveineuse") and 6 orals ("j'ai avalé", the short forms) came back `unknown`.
- `dose_has_unit` 98.6 % and `compare_pair` 100 % hold (the one miss: `0,25 g`, `true` predicted for `false`). `asked_<parameter>` misses: `auclast` asked and
  not found 6 times, `aucinf` found while not asked 5 times, `cmax`, `cl`, `vz` once each.

### Per tag (which kinds of hard requests break)

Sorted by the share of decisions right; the columns on the right are the questions that carry the failure. A request carries several tags.

| tag | requests | decisions right | `analysis` right | `auc_method` right | `route` right | `is_not_available` right | requests with all 20 right |
|---|---|---|---|---|---|---|---|
| dose-unit-g | 1 | 80.0 % | 0/1 | 0/1 | 1/1 | 1/1 | 0/1 |
| duration-unit-mismatch | 2 | 85.0 % | 0/2 | 0/2 | 0/2 | 2/2 | 0/2 |
| duration-word | 1 | 85.0 % | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 |
| multi-subject | 1 | 85.0 % | 0/1 | 0/1 | 1/1 | 1/1 | 0/1 |
| multiple-dose | 1 | 85.0 % | 1/1 | 1/1 | 0/1 | 0/1 | 0/1 |
| steady-state | 1 | 85.0 % | 1/1 | 1/1 | 0/1 | 0/1 | 0/1 |
| dose-unit-micro | 9 | 85.6 % | 0/9 | 0/9 | 2/9 | 9/9 | 0/9 |
| infusion | 7 | 85.7 % | 1/7 | 0/7 | 2/7 | 6/7 | 0/7 |
| route-implied | 5 | 87.0 % | 0/5 | 0/5 | 3/5 | 5/5 | 0/5 |
| unit-in-text | 5 | 87.0 % | 0/5 | 0/5 | 4/5 | 5/5 | 0/5 |
| parameter-not-in-schema | 2 | 87.5 % | 2/2 | 0/2 | 2/2 | 0/2 | 0/2 |
| plain | 2 | 87.5 % | 0/2 | 0/2 | 2/2 | 2/2 | 0/2 |
| route-stated | 8 | 88.1 % | 0/8 | 0/8 | 6/8 | 8/8 | 0/8 |
| colloquial | 6 | 88.3 % | 0/6 | 0/6 | 4/6 | 6/6 | 0/6 |
| invented | 16 | 88.8 % | 7/16 | 4/16 | 13/16 | 12/16 | 1/16 |
| out-of-scope | 4 | 88.8 % | 4/4 | 4/4 | 1/4 | 0/4 | 0/4 |
| parameter-not-for-route | 5 | 90.0 % | 5/5 | 0/5 | 5/5 | 0/5 | 0/5 |
| latin-route | 3 | 90.0 % | 0/3 | 0/3 | 3/3 | 3/3 | 0/3 |
| terminology-mismatch | 2 | 90.0 % | 0/2 | 0/2 | 2/2 | 2/2 | 0/2 |
| bioequivalence | 1 | 90.0 % | 1/1 | 1/1 | 0/1 | 0/1 | 0/1 |
| c0 | 1 | 90.0 % | 0/1 | 0/1 | 1/1 | 1/1 | 0/1 |
| dose-unit-mcg | 1 | 90.0 % | 0/1 | 0/1 | 1/1 | 1/1 | 0/1 |
| dose-unit-mg | 1 | 90.0 % | 0/1 | 0/1 | 1/1 | 1/1 | 0/1 |
| dose-without-unit | 1 | 90.0 % | 0/1 | 0/1 | 1/1 | 1/1 | 0/1 |
| iv-explicit | 1 | 90.0 % | 1/1 | 0/1 | 1/1 | 0/1 | 0/1 |
| no-dose | 1 | 90.0 % | 0/1 | 0/1 | 1/1 | 1/1 | 0/1 |
| population | 1 | 90.0 % | 1/1 | 1/1 | 0/1 | 0/1 | 0/1 |
| route-missing | 1 | 90.0 % | 0/1 | 0/1 | 1/1 | 1/1 | 0/1 |
| tlag | 1 | 90.0 % | 0/1 | 0/1 | 1/1 | 1/1 | 0/1 |
| unicode | 1 | 90.0 % | 0/1 | 0/1 | 1/1 | 1/1 | 0/1 |
| unit-conversion-in-text | 1 | 90.0 % | 0/1 | 0/1 | 1/1 | 1/1 | 0/1 |
| unit-variety | 1 | 90.0 % | 0/1 | 0/1 | 1/1 | 1/1 | 0/1 |
| unrecognized-unit | 1 | 90.0 % | 0/1 | 0/1 | 1/1 | 1/1 | 0/1 |
| urine | 1 | 90.0 % | 1/1 | 1/1 | 1/1 | 0/1 | 0/1 |
| abbreviation | 17 | 90.6 % | 5/17 | 1/17 | 16/17 | 16/17 | 0/17 |
| blq | 4 | 91.2 % | 0/4 | 1/4 | 4/4 | 4/4 | 0/4 |
| by-id | 2 | 92.5 % | 2/2 | 0/2 | 2/2 | 2/2 | 0/2 |
| two-requests-in-one-sentence | 2 | 92.5 % | 0/2 | 1/2 | 2/2 | 2/2 | 0/2 |
| typo | 2 | 92.5 % | 1/2 | 0/2 | 2/2 | 2/2 | 0/2 |
| compare | 8 | 93.8 % | 8/8 | 4/8 | 8/8 | 8/8 | 0/8 |
| follow-up | 4 | 95.0 % | 4/4 | 0/4 | 4/4 | 4/4 | 0/4 |
| rerun | 4 | 95.0 % | 3/4 | 4/4 | 4/4 | 4/4 | 0/4 |
| language-mix | 2 | 95.0 % | 1/2 | 1/2 | 2/2 | 2/2 | 1/2 |
| method-explicit | 2 | 95.0 % | 0/2 | 2/2 | 2/2 | 2/2 | 0/2 |
| english-term | 1 | 95.0 % | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 |
| no-parameter | 1 | 95.0 % | 1/1 | 0/1 | 1/1 | 1/1 | 0/1 |
| no-prior-analysis | 1 | 95.0 % | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 |
| non-auc-parameter | 1 | 95.0 % | 1/1 | 0/1 | 1/1 | 1/1 | 0/1 |
| recall | 1 | 95.0 % | 1/1 | 0/1 | 1/1 | 1/1 | 0/1 |
| simulate | 1 | 95.0 % | 0/1 | 1/1 | 1/1 | 1/1 | 0/1 |
| fit | 4 | 100.0 % | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| two-compartments | 2 | 100.0 % | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| oral | 1 | 100.0 % | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |

The tags do not separate the failures, the turn does: `analysis` is 0 for every tag made of first requests only (`dose-unit-micro` 0/9, `route-stated` 0/8,
`colloquial` 0/6, `route-implied` 0/5, `unit-in-text` 0/5, `abbreviation`, `typo`, ...) and right, by accident, on first requests whose gold is `none_needed`
(`out-of-scope`, `parameter-not-for-route`). What works is the follow-up (`follow-up`, `rerun`, `compare`) and the registered actions `fit` and `two-compartments`
(4 and 2 requests, every decision right). The worst tags by decisions (`dose-unit-g`, `duration-*`, `multi-subject`, `steady-state`) carry one more wrong cell (`route`,
`is_not_available`, `dose_has_unit`) on top of the `analysis` and `auc_method` collapse. The only 4 requests with no wrong decision are the 4 explicit fit
requests (ood-006, ood-007, ood-042, ood-066): no first NCA request is among them.

### Every wrong decision

143 wrong decisions on 70 of the 74 requests. 135 of the 143 have a probability of the predicted label of at least 0.90 (mean 0.98): the model is confidently
wrong. In the calibration table of the report, the 15 decisions below 0.9 are right 7 times, the 1465 above are right 90.8 %; ECE 0.093.

| request | text | wrong decisions: question gold -> predicted (probability of the predicted label) |
|---|---|---|
| ood-001 (turn 1) | J'ai pris un comprimé de 400 mg ce matin, voici mes concentrations. C'est quoi le Cmax et le Tmax ? | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-002 (turn 2) | et la t1/2 stp ? | `auc_method` linear -> not_applicable (1.00) |
| ood-003 (turn 2) | AUC0-t et AUC0-inf svp | `auc_method` linear -> not_applicable (1.00) |
| ood-004 (turn 1) | bolus IV de 200 mg ; quel est le Vd ? | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-005 (turn 1) | bolus de 200 mg : Cl/F ? | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-008 (turn 1) | Perfusion de 150 mg sur 2 h. Donne-moi le Cmax et l'AUC(0-t). | `analysis` nca -> none_needed (1.00); `asked_aucinf` false -> true (0.60); `auc_method` linear -> not_applicable (0.98); `route` iv_infusion -> unknown (1.00) |
| ood-009 (turn 2) | Et la MRT ? | `auc_method` linear -> not_applicable (1.00) |
| ood-010 (turn 1) | Perfusion de 500 µg pendant 1,5 h, Cmax et AUC0-inf. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00); `route` iv_infusion -> unknown (1.00) |
| ood-011 (turn 1) | Perfusion de 500 µg pendant 90 minutes : que vaut l'AUC(0-t) ? | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00); `route` iv_infusion -> unknown (1.00) |
| ood-012 (turn 1) | J'ai avalé 800 µg, les temps sont en minutes ; Cmax et AUC0-t. | `analysis` nca -> none_needed (1.00); `asked_aucinf` false -> true (0.59); `auc_method` linear -> not_applicable (1.00); `route` oral -> unknown (1.00) |
| ood-013 (turn 2) | Compare l'AUC linéaire et la lin-up/log-down. | `asked_auclast` true -> false (1.00) |
| ood-014 (turn 2) | Compare les deux AUC (valeur et %). | `asked_auclast` true -> false (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-015 (turn 2) | Compare l'analyse 2 à l'analyse 1. | `auc_method` lin_up_log_down -> not_applicable (1.00) |
| ood-016 (turn 1) | Voie orale, 300 mg : y a-t-il un Tlag ? | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-017 (turn 1) | Quel est le Tlag de ce bolus de 200 mg ? | `auc_method` linear -> not_applicable (1.00); `is_not_available` true -> false (1.00) |
| ood-018 (turn 1) | Quelle est la C0 après cette prise orale de 400 mg ? | `auc_method` linear -> not_applicable (1.00); `is_not_available` true -> false (1.00) |
| ood-019 (turn 1) | Ce produit de 400 mg est-il bioéquivalent au princeps ? | `is_not_available` true -> false (1.00); `route` oral -> unknown (1.00) |
| ood-020 (turn 1) | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. | `is_not_available` true -> false (1.00); `route` oral -> unknown (1.00) |
| ood-021 (turn 1) | Après une prise orale, voici mes concentrations : quelle est la demi-vie ? | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-022 (turn 1) | Prise orale de 100, voici les données. Cmax ? | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-023 (turn 1) | Bolus IV de 2 mg : donne-moi la clairance et le Vz. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-024 (turn 1) | Bolus de 2000 mcg : CL et Vz. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-025 (turn 2) | Et le pourcentage d'AUC extrapolée ? | `auc_method` linear -> not_applicable (1.00) |
| ood-026 (turn 1) | Il y a un zéro sous la LLOQ dans le tableau, on le garde ? Donne l'AUC(0-t) et la Cmax, dose orale 50 mg. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (0.88) |
| ood-027 (turn 1) | Simule les concentrations après une dose orale de 300 mg. | `analysis` simulate -> none_needed (0.55) |
| ood-028 (turn 1) | Donne-moi d'abord la demi-vie, ensuite la clairance et le Vz, pour cette dose orale de 300 mg. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-029 (turn 1) | Donne-moi le Cmax puis refais l'analyse en lin-up/log-down, bolus de 300 mg. | `analysis` nca -> none_needed (0.92) |
| ood-030 (turn 2) | Refais l'analyse en lin-up/log-down et compare les deux AUC en valeur et en %. | `asked_auclast` true -> false (1.00) |
| ood-031 (turn 1) | Peux-tu me donner le Cmax, le Tmax et le t1/2 after a single oral dose of 100 mg ? | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-032 (turn 1) | kel est le Cmax é le Tmax de ce tablo ? dose 400 mg per os | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-033 (turn 1) | Dose orale de 500 mg : AUC0-∞ et AUC0-t. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-034 (turn 1) | Bolus de 150 mg : quel est le Vdss ? | `asked_vz` false -> true (1.00); `auc_method` linear -> not_applicable (1.00); `is_not_available` true -> false (1.00) |
| ood-035 (turn 1) | Bolus de 150 mg : le R² ajusté et le nombre de points de la régression terminale. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-036 (turn 1) | Prise unique de 100 mg par voie orale : je veux le MRT et la demi-vie. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-037 (turn 1) | Perfusion de 150 mg sur 2 h : clairance et volume de distribution. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00); `route` iv_infusion -> unknown (1.00) |
| ood-038 (turn 1) | Quel est le Tlag de cette perfusion de 150 mg ? | `auc_method` linear -> not_applicable (1.00); `is_not_available` true -> false (1.00) |
| ood-039 (turn 1) | Dose IV de 1000 µg : AUC(0-inf) et pourcentage extrapolé. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-040 (turn 1) | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00); `route` oral -> unknown (1.00) |
| ood-041 (turn 1) | Bolus de 200 mg à t=0, temps en minutes : Cmax et Tmax. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-043 (turn 1) | Perfusion IV de 150 mg sur 2 h, CL et Vz svp. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-044 (turn 1) | Comprimé à libération prolongée de 5000 µg : Cmax, Tmax et demi-vie. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00); `route` oral -> unknown (1.00) |
| ood-045 (turn 1) | Bolus de 300 mg, temps en minutes : AUC(0-t) et clairance. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (0.97) |
| ood-046 (turn 1) | Bolus de 150 mg : le Cl/F et le Vz/F ? | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-047 (turn 1) | Voie orale, 100 mg : λz et t½. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-048 (turn 1) | Voie orale, 300 mg : quelle est la constante d'absorption ka ? | `auc_method` linear -> not_applicable (1.00); `is_not_available` true -> false (1.00) |
| ood-049 (turn 1) | Cmax et nombre de points de la régression terminale, dose orale de 100 mg. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-050 (turn 1) | AUC(0-t) par la méthode lin-up/log-down, dose orale de 50 mg. | `analysis` nca -> none_needed (1.00) |
| ood-051 (turn 1) | Bolus de 2000 µg : l'AUC(0-t) tient-elle compte du point sous la LLOQ ? et le % extrapolé ? | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-052 (turn 1) | Dose orale de 500 mg, méthode des trapèzes linéaires : AUC0-t. | `analysis` nca -> none_needed (1.00) |
| ood-053 (turn 1) | Voici mes concentrations après 400 mg ; quel est le Cmax ? | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-054 (turn 1) | Après une injection intraveineuse directe de 200 mg : C0 et Vz. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-055 (turn 1) | Perfusion de 500 µg sur 90 min : Cmax. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00); `route` iv_infusion -> unknown (1.00) |
| ood-056 (turn 2) | Rappelle-moi la dose et la méthode d'AUC utilisées. | `auc_method` linear -> not_applicable (1.00) |
| ood-057 (turn 2) | Compare le Cmax entre les deux méthodes. | `auc_method` linear -> not_applicable (1.00) |
| ood-058 (turn 1) | Compare les AUC linéaire et lin-up/log-down, dose orale de 400 mg. | `asked_auclast` true -> false (0.99) |
| ood-059 (turn 1) | 250 mg per os, voici les concentrations en µg/mL : Cmax, Tmax et AUC0-inf. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (0.98) |
| ood-060 (turn 1) | Bolus IV de 120 mg : quel est le Tlag ? | `auc_method` linear -> not_applicable (1.00); `is_not_available` true -> false (1.00) |
| ood-061 (turn 1) | Quelle est la C0 après cette prise orale de 200 mg ? | `auc_method` linear -> not_applicable (1.00); `is_not_available` true -> false (1.00) |
| ood-062 (turn 1) | Perfusion de 75 mg sur 1,5 h, les temps sont en minutes : Cmax. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00); `route` iv_infusion -> unknown (1.00) |
| ood-063 (turn 1) | Étude à deux sujets, 300 mg par voie orale : Cmax et AUC0-t par sujet. | `analysis` nca -> none_needed (1.00); `asked_aucinf` false -> true (0.67); `auc_method` linear -> not_applicable (0.97) |
| ood-064 (turn 1) | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. | `asked_cmax` false -> true (1.00); `is_not_available` true -> false (1.00); `route` oral -> unknown (1.00) |
| ood-065 (turn 1) | Recueil urinaire : quantité excrétée et clairance rénale. | `asked_cl` false -> true (1.00); `is_not_available` true -> false (1.00) |
| ood-067 (turn 1) | Voie orale 1200 mg, temps en minutes : t1/2 et MRT. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |
| ood-068 (turn 1) | 80 mg per os, il y a des zéros sous la LLOQ : AUC(0-t) et Cmax. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (0.99) |
| ood-069 (turn 1) | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. | `analysis` nca -> none_needed (1.00); `asked_aucinf` false -> true (0.56); `auc_method` linear -> not_applicable (0.97); `dose_has_unit` false -> true (1.00) |
| ood-070 (turn 1) | Perfusion de 750 µg sur 1 h : Vz et CL. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00); `route` iv_infusion -> unknown (1.00) |
| ood-071 (turn 2) | Compare l'AUC linéaire et la lin-up/log-down. | `asked_auclast` true -> false (1.00) |
| ood-072 (turn 2) | Compare l'analyse 2 et l'analyse 1 pour l'AUC. | `asked_auclast` true -> false (1.00); `auc_method` lin_up_log_down -> not_applicable (0.65) |
| ood-073 (turn 1) | Prise orale de 200 mg : Cmax, Tmax et AUC0-t. | `analysis` nca -> none_needed (1.00); `asked_aucinf` false -> true (0.84); `auc_method` linear -> not_applicable (0.97) |
| ood-074 (turn 1) | Bolus de 120 mg : Cmax et AUC0-inf. | `analysis` nca -> none_needed (1.00); `auc_method` linear -> not_applicable (1.00) |

### Harness answers (one fresh Caladrius session per request, prior analyses replayed first)

| | trained model | gold decisions |
|---|---|---|
| answers with values | 12 | 41 |
| "Aucune analyse n'est encore faite" (`refusal:no-analysis`) | 58 | 1 |
| asked back (dose unit, route, duration: `refusal:ask`) | 0 | 13 |
| parameter not available (`refusal:not-available`) | 0 | 11 |
| not wired (fit, simulate) | 4 | 5 |
| which pair (`refusal:which-pair`) | 0 | 3 |
| errors | 0 | 0 |

All 12 answers of the model are follow-ups (turn 2): not one of the 62 first requests got a value, and 58 of them were told that no analysis exists. Nothing that
should have been refused or asked back was answered ("the dangerous direction": 0), no decision came back outside the offered options, and the state rebuilt by the
harness equals the scored row on the 74 requests. The harness is not at 74/74 even with the right decisions: with the gold decisions it refuses or asks 12
requests whose gold expects values (ood-008, 010, 011, 037, 043, 055, 062, 070: infusion duration not parsed; ood-013, 030, 071: a compare with a single prior
analysis asks the pair again; ood-058: compare with no prior analysis; the reviewer's Part 2 explains these), so 41 answers is the ceiling on this set. One answer
to read: ood-003 asked "AUC0-t et AUC0-inf" and got AUC(0-inf) only (`asked_auclast` wrong), a silent omission rather than a wrong number.

**What a human must read** (70 of 74 requests)

Wrong decisions in the run, answers that contradict the gold decisions, errors, and the requests of the tags that broke (at most 6 per tag). Every other answer is in `answers.jsonl`; a correct decision does not make a correct answer, so read at least a few of them.


- ood-001 (ex02_oral_1, turn 1; tags: colloquial, route-implied): wrong decision: analysis, auc_method, route; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: colloquial; tag that broke: route-implied
- ood-002 (ex02_oral_1, turn 2; tags: abbreviation, typo, follow-up): wrong decision: auc_method; tag that broke: abbreviation; tag that broke: typo; tag that broke: follow-up
- ood-003 (ex02_oral_1, turn 2; tags: abbreviation, follow-up): wrong decision: asked_auclast, auc_method; tag that broke: abbreviation; tag that broke: follow-up
- ood-004 (ex01_iv_bolus, turn 1; tags: abbreviation, route-stated): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: abbreviation; tag that broke: route-stated
- ood-005 (ex01_iv_bolus, turn 1; tags: abbreviation, terminology-mismatch): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: abbreviation; tag that broke: terminology-mismatch
- ood-008 (ex05_iv_infusion, turn 1; tags: infusion, route-stated): wrong decision: analysis, auc_method, route; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: infusion; tag that broke: route-stated
- ood-009 (ex05_iv_infusion, turn 2; tags: abbreviation, follow-up): wrong decision: auc_method; tag that broke: abbreviation; tag that broke: follow-up
- ood-010 (ex12_iv_infusion, turn 1; tags: dose-unit-micro, duration-unit-mismatch, unit-in-text): wrong decision: analysis, asked_auclast, auc_method, route; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: dose-unit-micro; tag that broke: duration-unit-mismatch; tag that broke: unit-in-text
- ood-011 (ex12_iv_infusion, turn 1; tags: duration-word, colloquial, dose-unit-micro): wrong decision: analysis, auc_method, route; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: duration-word; tag that broke: colloquial; tag that broke: dose-unit-micro
- ood-012 (ex08_oral_1, turn 1; tags: abbreviation, route-implied, dose-unit-micro): wrong decision: analysis, auc_method, route; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: abbreviation; tag that broke: route-implied; tag that broke: dose-unit-micro
- ood-013 (ex08_oral_1, turn 2; tags: compare, english-term, rerun): wrong decision: asked_auclast; tag that broke: compare; tag that broke: english-term; tag that broke: rerun
- ood-014 (ex08_oral_1, turn 2; tags: compare): wrong decision: asked_auclast, auc_method; tag that broke: compare
- ood-015 (ex08_oral_1, turn 2; tags: compare, by-id, no-parameter): wrong decision: auc_method; tag that broke: compare; tag that broke: by-id; tag that broke: no-parameter
- ood-016 (ex04_oral_1_lag, turn 1; tags: route-stated, tlag): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: route-stated; tag that broke: tlag
- ood-017 (ex01_iv_bolus, turn 1; tags: parameter-not-for-route, iv-explicit): wrong decision: auc_method, is_not_available; tag that broke: parameter-not-for-route; tag that broke: iv-explicit
- ood-018 (ex02_oral_1, turn 1; tags: parameter-not-for-route): wrong decision: auc_method, is_not_available; tag that broke: parameter-not-for-route
- ood-019 (ex02_oral_1, turn 1; tags: out-of-scope, bioequivalence): wrong decision: is_not_available, route; tag that broke: out-of-scope; tag that broke: bioequivalence
- ood-020 (ex02_oral_1, turn 1; tags: out-of-scope, population): wrong decision: is_not_available, route; tag that broke: out-of-scope; tag that broke: population
- ood-021 (ex06_oral_0, turn 1; tags: no-dose, route-implied): wrong decision: analysis, auc_method; tag that broke: no-dose; tag that broke: route-implied
- ood-022 (ex06_oral_0, turn 1; tags: dose-without-unit): wrong decision: analysis, auc_method; tag that broke: dose-without-unit
- ood-023 (ex07_iv_bolus, turn 1; tags: unit-conversion-in-text, dose-unit-mg): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: unit-conversion-in-text; tag that broke: dose-unit-mg
- ood-024 (ex07_iv_bolus, turn 1; tags: dose-unit-mcg, unrecognized-unit): wrong decision: analysis, auc_method; tag that broke: dose-unit-mcg; tag that broke: unrecognized-unit
- ood-025 (ex07_iv_bolus, turn 2; tags: follow-up, abbreviation): wrong decision: auc_method; tag that broke: follow-up
- ood-026 (ex13_oral_1, turn 1; tags: blq, colloquial): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: blq; tag that broke: colloquial
- ood-027 (ex09_pk2_oral_1, turn 1; tags: simulate): wrong decision: analysis; tag that broke: simulate
- ood-028 (ex09_pk2_oral_1, turn 1; tags: two-requests-in-one-sentence): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: two-requests-in-one-sentence
- ood-029 (ex03_pk2_iv_bolus, turn 1; tags: two-requests-in-one-sentence, rerun): wrong decision: analysis; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: two-requests-in-one-sentence; tag that broke: rerun
- ood-030 (ex03_pk2_iv_bolus, turn 2; tags: compare, rerun): wrong decision: asked_auclast; tag that broke: compare; tag that broke: rerun
- ood-031 (ex10_oral_1_lag, turn 1; tags: language-mix, abbreviation): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer
- ood-032 (ex02_oral_1, turn 1; tags: typo, colloquial, latin-route): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: typo; tag that broke: colloquial; tag that broke: latin-route
- ood-033 (ex17_oral_1, turn 1; tags: abbreviation): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer
- ood-034 (ex14_iv_bolus, turn 1; tags: parameter-not-in-schema, abbreviation): wrong decision: asked_vz, auc_method, is_not_available; tag that broke: parameter-not-in-schema
- ood-035 (ex14_iv_bolus, turn 1; tags: abbreviation): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer
- ood-036 (ex25_oral_1, turn 1; tags: abbreviation): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer
- ood-037 (ex05_iv_infusion, turn 1; tags: infusion, route-stated): wrong decision: analysis, auc_method, route; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: infusion; tag that broke: route-stated
- ood-038 (ex05_iv_infusion, turn 1; tags: parameter-not-for-route, infusion): wrong decision: auc_method, is_not_available; tag that broke: parameter-not-for-route; tag that broke: infusion
- ood-039 (ex11_pk2_iv_bolus, turn 1; tags: dose-unit-micro, route-stated): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: dose-unit-micro; tag that broke: route-stated
- ood-040 (ex16_pk2_oral_1, turn 1; tags: colloquial, dose-unit-micro): wrong decision: analysis, auc_method, route; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: colloquial; tag that broke: dose-unit-micro
- ood-041 (ex18_pk2_iv_bolus, turn 1; tags: route-stated, unit-in-text): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: route-stated; tag that broke: unit-in-text
- ood-043 (ex20_iv_infusion, turn 1; tags: infusion, abbreviation): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: infusion
- ood-044 (ex21_oral_0, turn 1; tags: dose-unit-micro, route-implied): wrong decision: analysis, auc_method, route; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: dose-unit-micro; tag that broke: route-implied
- ood-045 (ex23_iv_bolus, turn 1; tags: route-stated, unit-in-text): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: unit-in-text
- ood-046 (ex24_pk2_iv_bolus, turn 1; tags: terminology-mismatch, abbreviation): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: terminology-mismatch
- ood-047 (ex25_oral_1, turn 1; tags: abbreviation, unicode): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: unicode
- ood-048 (ex04_oral_1_lag, turn 1; tags: parameter-not-in-schema): wrong decision: auc_method, is_not_available; tag that broke: parameter-not-in-schema
- ood-049 (ex06_oral_0, turn 1; tags: route-stated): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer
- ood-050 (ex13_oral_1, turn 1; tags: method-explicit, blq): wrong decision: analysis; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: method-explicit; tag that broke: blq
- ood-051 (ex07_iv_bolus, turn 1; tags: blq, colloquial, dose-unit-micro): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: blq; tag that broke: colloquial
- ood-052 (ex22_pk2_oral_1, turn 1; tags: method-explicit, abbreviation): wrong decision: analysis; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: method-explicit
- ood-053 (ex02_oral_1, turn 1; tags: route-missing): wrong decision: analysis, auc_method; tag that broke: route-missing
- ood-054 (ex01_iv_bolus, turn 1; tags: route-implied, c0): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: route-implied; tag that broke: c0
- ood-055 (ex12_iv_infusion, turn 1; tags: infusion, dose-unit-micro): wrong decision: analysis, auc_method, route; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: infusion
- ood-056 (ex02_oral_1, turn 2; tags: recall): wrong decision: auc_method; tag that broke: recall
- ood-057 (ex03_pk2_iv_bolus, turn 2; tags: compare, non-auc-parameter): wrong decision: auc_method; tag that broke: compare; tag that broke: non-auc-parameter
- ood-058 (ex02_oral_1, turn 1; tags: compare, no-prior-analysis): wrong decision: asked_auclast; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: compare; tag that broke: no-prior-analysis
- ood-059 (oodx01_oral_mg_ugml, turn 1; tags: invented, unit-variety, latin-route): wrong decision: analysis, asked_auclast, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: unit-variety; tag that broke: latin-route
- ood-060 (oodx02_iv_bolus_tlag, turn 1; tags: invented, parameter-not-for-route): wrong decision: auc_method, is_not_available; tag that broke: parameter-not-for-route
- ood-061 (oodx03_oral_c0, turn 1; tags: invented, parameter-not-for-route): wrong decision: auc_method, is_not_available; tag that broke: parameter-not-for-route
- ood-062 (oodx04_infusion_dur_h, turn 1; tags: invented, duration-unit-mismatch, infusion): wrong decision: analysis, auc_method, route; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: duration-unit-mismatch; tag that broke: infusion
- ood-063 (oodx05_two_subjects, turn 1; tags: invented, multi-subject): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: multi-subject
- ood-064 (oodx06_steady_state, turn 1; tags: invented, out-of-scope, steady-state, multiple-dose): wrong decision: asked_cmax, is_not_available, route; tag that broke: out-of-scope; tag that broke: steady-state; tag that broke: multiple-dose
- ood-065 (oodx07_urine, turn 1; tags: invented, out-of-scope, urine): wrong decision: asked_cl, is_not_available; tag that broke: out-of-scope; tag that broke: urine
- ood-067 (oodx09_oral_min_ng, turn 1; tags: invented, abbreviation, unit-in-text): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: unit-in-text
- ood-068 (oodx10_oral_blq, turn 1; tags: invented, blq, latin-route): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: blq; tag that broke: latin-route
- ood-069 (oodx11_oral_dose_g, turn 1; tags: invented, dose-unit-g, unit-in-text): wrong decision: analysis, auc_method, dose_has_unit; tag that broke: dose-unit-g; tag that broke: unit-in-text
- ood-070 (oodx12_iv_infusion_mcg, turn 1; tags: invented, dose-unit-micro, infusion): wrong decision: analysis, auc_method, route; refused / asked (no-analysis) where the gold decisions expect an answer
- ood-071 (oodx01_oral_mg_ugml, turn 2; tags: invented, compare, rerun): wrong decision: asked_auclast; tag that broke: rerun
- ood-072 (oodx09_oral_min_ng, turn 2; tags: invented, compare, by-id): wrong decision: asked_auclast, auc_method; tag that broke: by-id
- ood-073 (oodx03_oral_c0, turn 1; tags: invented, plain): wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: plain
- ood-074 (oodx02_iv_bolus_tlag, turn 1; tags: invented, plain): wrong decision: analysis, asked_auclast, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: plain

(Every request with its answer, its decisions and the reason is in `ood/runs/2026-10-10-qwen35-0.8b/report.md`; the 70 requests above are the tool's list.)

### Reading

1. The model does not transfer to unfamiliar wording. On first requests it never says `nca` (0 of 45), so 58 of 62 first requests end in "no analysis yet" and
   nothing is computed; only follow-ups (`analysis` 12/12) and fit and compare wordings, which resemble the 83 training sentences, work.
2. Collapsed: `analysis` (37.8 %), `auc_method` (21.6 %, a consequence), `is_not_available` (recall 0/11, score equal to the constant), `route` on infusions (3/10).
   Held: `compare_pair`, `dose_has_unit` and the 14 `asked_<parameter>` booleans (98.6 %).
3. The reviewer's predictions were wrong in size and in order. About 80 % per question was expected: the model has 74.9 % macro, below the best constant (79.3 %) and
   below the reviewer's own rules (88.8 %); whole request 5.4 % (4/74) against 30 %. `is_not_available` (predicted first to break, 55 %) did break, every positive is
   missed, but its score equals the constant (85.1 %); the first real break is `analysis` on first requests (82 % predicted, 37.8 %), then `auc_method` (72 %, 21.6 %).
   `dose_has_unit` (78 % predicted, 98.6 %) and `compare_pair` (80 %, 100 %) did better than expected.
4. The 99.9 % held-out and the 175/175 are memorisation figures, as the reviewer argued (720/720 held-out requests are verbatim in train): what they measure is the
   83 sentences of the generator.
5. The 0.8B model's confidence does not warn about any of this (135 of 143 wrong decisions at 0.90 or more), so a threshold on that probability cannot be the gate.

## Harness fixes after the review (2026-10-10)

Item 4 of the reordered next steps (`PLAN.md`): the six defects the reviewer found by running its 74 requests through the gold path
(`ood/REVIEW.md`), each fixed in `harness.py` with a regression test built from the failing request (`tests/test_decision_harness.py`,
class `TestReviewDefects`).

| # | defect (request) | fix |
|---|---|---|
| 1 | infusion duration read in 0 of 8 natural wordings (ood-008, 010, 011, 037, 043, 055, 062, 070) | `parse_duration` reads a number and a time unit anywhere in the first message (dose sentence, then request): "sur 2 h", "pendant 1,5 h", "90 minutes", "perfusée sur 1 h", "en 2 heures", decimal comma; with several, the first after "perfus". Absent: asked (`T_ASK_DURATION`). In another time unit than the data: asked again in the data's unit, as before (the harness converts nothing; ood-010, ood-062) |
| 2 | compare direction `2+1` unrepresentable (ood-015, ood-072) | `questions_for` offers both orders (`2+3`, `3+2`; a = reference, b - a); `analysis_compare` gets a and b in that order; the first line of the answer names the reference |
| 3 | the refusal named the first parameter in table order ("Cmax n'est pas calculé" for Cmax + C0) | checked parameter by parameter on the reference analysis: computed ones are given, the others refused by name with the engine's reason; an NCA turn lets the engine say which; before any analysis one parameter is refused by name, several are not guessed (`T_NOT_AVAILABLE_UNCHECKED`) |
| 4 | "no dose" answered "the dose has no unit" (ood-021) | the dose is read first: no number at all -> `T_ASK_DOSE`; a number without unit, or `dose_has_unit` = false -> `T_ASK_DOSE_UNIT` ("pas d'unité que je reconnaisse"); the dose pattern also reads g, mcg, ng |
| 5 | out-of-scope asks got "not calculated for this route" (ood-019, 020, 064, 065) | new `analysis` option `not_supported` -> `T_NOT_SUPPORTED` (says what the harness does and that it gives no value); `is_not_available` = true with no parameter asked, the reviewer's encoding, gets the same answer |
| 6 | "2 mg" on a 2000 µg exercise ran dose = 2 silently (ood-023) | the header prints the dose with the user's unit ("dose 2 mg"). When the dose's mass unit is not the concentrations' (mg or µg against ng/mL), Caladrius receives the units (`nca_run` option `units`: time, concentration, dose) in a second session and each value labelled "dose unit/..." is followed by its conversion: "0.0110019 dose unit/(h*ng/mL), soit 11.0019 L/h (conversion faite par Caladrius avec la dose en mg)". The analysis of record still gets the amount only (the oracle's convention), and the second session keeps the conversation's analysis ids; its calls are in `unit_log`, outside the tool-call counts |

`run_harness.py --decider gold-asked` (the wording of the reviewer's brief) is now accepted as `gold`.

**Dataset.** `analysis` gains `not_supported` and `compare_pair` the reversed pairs. The generator writes no out-of-scope request and no
reversed compare, so no row is relabelled: regeneration gives the same 1980 / 720 / 900 rows with the same ids, states, factors and labels,
only `questions` and the zero probabilities of the new options in `gold` differ, and the counts block is unchanged. The test that every
declared option has train rows lists these two as the known gaps. **Closed by dataset v2** (same day, Step 1 above): out-of-scope,
directed-compare, one-line, implied-route and dose-without-unit wordings, and a wording-level split.

**Retraining.** The trained 0.8B must be retrained before any trained figure is quoted on this schema: its prompt now lists 7 `analysis`
options and both pair orders (the option numbering shifts), and it never saw a positive `not_supported` or `3+2`. Retraining on the current
generator would only teach it never to choose them: the generator needs out-of-scope and reversed-compare wordings first (Step 6 shows the
wording problem is wider anyway). Not re-measured here (no GPU used). Dataset v2 has them; the retraining is on `train.jsonl` v2.

**Ceiling** (`python decision/run_harness.py --decider gold`, [`runs/2026-10-10-harness-gold-asked/`](runs/2026-10-10-harness-gold-asked/report.md)):
**175 / 175 oracle turns, 558 / 558 numbers**, 0 / 250 invalid or failed calls, 0 / 75 deviating calls, gate 0 / 778 unverified, 0.002 s
per turn. The units session made 36 calls in the 18 exercises whose dose is mg or µg against ng/mL. `score_turn` first counted 178 / 200
turns correct: the 22 others were the import and clearance turns of the 11 mg-against-ng/mL exercises, where its `must_not` rule ("CL x 10^3",
"Vz x 10^3", written against a model that converts by itself) fired on Caladrius's L/h and L values, the only 22 scorer/oracle
disagreements. **Fixed (2026-10-10):** `score_turn` takes the tool results of the turn and does not count a `must_not` value when every
number of the answer that hits it is written verbatim in one of them (`forbidden_from_tools` lists it); `run_harness.py` passes the turn's
calls and the units session's results (a cache: the clearance turn reuses the conversion of turn 1) and now stores the units session's
results in `unit_calls`, which `run_bench.py --rescore` reads. The stored run had no units-session results, so it was rerun with the gold
decider (no model, same folder): **200 / 200 scorer turns, 175 / 175 oracle turns, 558 / 558 numbers, 0 disagreements**, 22 turns with
`forbidden_from_tools`; `run_bench.rescore` on the stored records changes nothing. The 27B runs were not rescored.

**The reviewer's 74 requests, gold decisions.** `eval_ood.py --decider gold` (outputs redirected to
[`runs/2026-10-10-ood-gold/`](runs/2026-10-10-ood-gold/report.md); `ood/` untouched): `--no-run` 1480 / 1480 decisions, 74 / 74 rows; the
run gives 47 answers and 27 refusals or questions, 0 errors, 0 answers where a refusal is expected. Six requests are refused where an answer
is expected. ood-010 and 062 give the duration in h on data in min, so it is asked again in min. ood-013, 030 and 071 compare after a single
analysis: the harness re-runs, re-asks, and the stateless gold says `not_applicable` (open item (b)). ood-058 asks for a compare with no
analysis. With the reviewer's own gold path (the state, gold decider and expected branch of `ood/run_ood_goldpath.py`, imported unchanged; its loop
rerun from a copy outside the repository that writes nothing under `ood/` and also classifies the new templates):

- **64 / 64** of the lines it counted as intended still behave as intended. Three intents are the corrected ones: ood-021 now asks for
  the dose; ood-019, 020, 064 and 065 get `not_supported`; ood-023 says "dose 2 mg" and shows 11.0019 L/h.
- All **10** it did not count now behave as intended. The 6 infusions with a duration in the data's unit run. ood-010 and 062 ask for the
  duration in minutes; the reviewer's expected branch was an answer, so by its letter the count is 72 / 74. ood-015 and 072 compare 3
  against 2 in the user's order.
- `eval_ood.py` sorted a gold pair (`translate_pair`), so its rows lost the direction of ood-015 and 072, and it filed `T_NOT_SUPPORTED`
  under `refusal:not-wired` because both templates start "Cette demande (". **Fixed (2026-10-10)**, with tests: the pair keeps the user's
  order ("2+1" renumbered "3+2"), `T_NOT_SUPPORTED` is `refusal:not-supported` and a gold `not_supported` expects a refusal.
  `ood/rows.jsonl` was not regenerated (the Bonsai run of the same day reads it): `python decision/eval_ood.py --convert-only` updates
  the 74 rows to the current question set (7 `analysis` options, both pair orders) and the direction of ood-015 and 072.
