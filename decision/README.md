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

`workflow` = `pk_analysis_requests`, 7 questions per row, no `score` question (nothing in the closed set is graded). `state` is a digest of
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
| `parameter_asked` | choice | cmax, tmax, c0, auclast, aucinf, lambda_z, half_life, cl, vz, mrt, aucpext, lambda_z_points, adj_r2, tlag, several, none | parameters named by the wording (one key => that key, two or more => several, none for a recall or a simulation) |
| `dose_has_unit` | noul | false, true | whether the dose sentence carries mg / ug |
| `is_not_available` | noul | false, true | true exactly for the `not_available` kind: the parameter asked (C0 after an oral dose, Tlag or C0 after an IV dose) is in `ground_truth.nca.linear.not_calculated` of `meta.json` |
| `compare_pair` | choice | `not_applicable` and one key `a+b` per pair of analysis ids present (`2+3`); `none_available` when fewer than two analyses exist | true only on the compare turn |

Turn kinds: the 8 scripted ones of `bench/scripts.py` (import_nca, cmax_tmax, clearance_volume, half_life, lambda_z_regression, recall,
compare, not_available) and 4 extra kinds written for this dataset so that every option of `analysis` and `parameter_asked` has examples:
`nca_other` (AUC(0-inf), MRT, AUC(0-tlast), lambda_z read from the NCA already run), `fit_pk1`, `fit_pk2`, `simulate`.

Per (exercise, kind): the scripted wording (scripted kinds only, verbatim from `bench/scripts.py`) and 2 hand-written French paraphrases
(3 for the extra kinds), picked among 4 to 5 wordings per kind (`WORDINGS` in `make_dataset.py`), some of which ask one parameter only.
Paraphrased rows also use 5 hand-written introductions of the data, 3 phrasings of each route, and in 20 % of them drop the unit of the
dose, in 20 % the route (not on `not_available` rows, where the route decides the answer). Conventions of the state: the compare turn is
described after the harness ran the requested re-run (analyses 2 and 3 present); in 40 % of the rows of the result-reading kinds both
analyses are present too (the question comes later in the conversation); a `simulate` state holds a fit as analysis 3.

## Exercises and split

- `bench/exercises/`: the 25 benchmark exercises (read only here); rows carry `factors.bench = true`.
- `decision/exercises/`: 75 more, 3 seeds (31415926, 27182818, 16180339) of the same plan, generated by `decision/make_exercises.py`
  with `bench/make_exercises.py` (the benchmark seed is 20261009; a draw the oracle rejects is redrawn, see `meta.json` `attempt`).
- Split by exercise, never by row: 20 whole exercises drawn with seed 20261010 among the 75 new ones are `heldout.jsonl`; the other 80
  exercises (the 25 of the benchmark included) are `train.jsonl`. The harness rules are written against the benchmark and never see the held-out ones.
- Caution for step 5: the benchmark exercises are in the training set, so a decision model scored on them is scored in-sample. Its clean
  figures are the held-out ones; filter `factors.bench` to train without them.

## Regenerate

```
python decision/make_exercises.py     # only to rebuild decision/exercises/ (needs caladrius-mcp, see apothicaire.MCP_BIN); byte-identical for the same engine
python decision/make_dataset.py       # decision/data/train.jsonl, decision/data/heldout.jsonl, and the counts block below; no engine needed
python -m unittest tests.test_decision_dataset   # the tests are unittest-based like the others (pytest is not installed here, but collects them)
```

`decision/data/` is git-ignored (22 MB, deterministic); the exercises are versioned.

## Counts (class balance)

<!-- counts:begin -->

| file | rows | exercises |
|---|---|---|
| train.jsonl | 2880 | 80 |
| heldout.jsonl | 720 | 20 |

`analysis`

| answer | train | heldout |
|---|---|---|
| compare | 240 | 60 |
| fit_pk1 | 240 | 60 |
| fit_pk2 | 240 | 60 |
| nca | 240 | 60 |
| none_needed | 1680 | 420 |
| simulate | 240 | 60 |

`route`

| answer | train | heldout |
|---|---|---|
| iv_bolus | 761 | 231 |
| iv_infusion | 275 | 89 |
| oral | 1416 | 314 |
| unknown | 428 | 86 |

`auc_method`

| answer | train | heldout |
|---|---|---|
| lin_up_log_down | 240 | 60 |
| linear | 240 | 60 |
| not_applicable | 2400 | 600 |

`parameter_asked`

| answer | train | heldout |
|---|---|---|
| adj_r2 | 36 | 9 |
| aucinf | 60 | 11 |
| auclast | 283 | 73 |
| aucpext | 28 | 9 |
| c0 | 154 | 33 |
| cl | 36 | 13 |
| cmax | 30 | 7 |
| half_life | 69 | 16 |
| lambda_z | 46 | 12 |
| lambda_z_points | 66 | 16 |
| mrt | 42 | 12 |
| none | 480 | 120 |
| several | 1404 | 349 |
| tlag | 95 | 28 |
| tmax | 20 | 4 |
| vz | 31 | 8 |

`dose_has_unit`

| answer | train | heldout |
|---|---|---|
| false | 467 | 131 |
| true | 2413 | 589 |

`is_not_available`

| answer | train | heldout |
|---|---|---|
| false | 2640 | 660 |
| true | 240 | 60 |

`compare_pair`

| answer | train | heldout |
|---|---|---|
| 2+3 | 240 | 60 |
| not_applicable | 2640 | 660 |

<!-- counts:end -->

## Limits

- The turns are the scripted ones of the benchmark plus 4 extra kinds: the questions are templates, the dataset teaches the model the
  intent behind a fixed set of sentences, not free French. The paraphrases (4 to 5 per kind, 5 introductions) are written by hand, no
  model; they vary the wording, not the register or the typos of real students.
- Class balance is poor by construction: `is_not_available` is true on 1 row out of 12, `compare_pair` is `not_applicable` on 11 out of 12,
  `none_needed` is 58 % of `analysis`. Single-parameter answers are a few dozen rows each.
- Labels are decided by the generator, not by annotators: one-hot gold, so calibration on this set measures the model against a
  certain truth, not against annotator disagreement; ambiguous requests (a user who gives no AUC method, no unit and no route) are not covered.
- `route` = `unknown` and `dose_has_unit` = false come from synthetic omissions in the sentence, not from the exercise data.
- Exercises are single-subject, one dose, simulated one- and two-compartment models with proportional noise; no multi-subject files,
  no wrong-unit CSV headers, no data error.
