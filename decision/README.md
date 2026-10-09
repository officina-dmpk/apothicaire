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

`parameter_asked`

| answer | train | heldout | bench |
|---|---|---|---|
| adj_r2 | 24 | 9 | 12 |
| aucinf | 39 | 11 | 21 |
| auclast | 194 | 73 | 89 |
| aucpext | 19 | 9 | 9 |
| c0 | 104 | 33 | 50 |
| cl | 23 | 13 | 13 |
| cmax | 23 | 7 | 7 |
| half_life | 46 | 16 | 23 |
| lambda_z | 33 | 12 | 13 |
| lambda_z_points | 47 | 16 | 19 |
| mrt | 31 | 12 | 11 |
| none | 330 | 120 | 150 |
| several | 963 | 349 | 441 |
| tlag | 67 | 28 | 28 |
| tmax | 16 | 4 | 4 |
| vz | 21 | 8 | 10 |

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
  Single-parameter answers are a few dozen rows each.
- Labels are decided by the generator, not by annotators: one-hot gold, so calibration on this set measures the model against a
  certain truth, not against annotator disagreement; ambiguous requests (a user who gives no AUC method, no unit and no route) are not covered.
- `route` = `unknown` and `dose_has_unit` = false come from synthetic omissions in the sentence, not from the exercise data.
- Exercises are single-subject, one dose, simulated one- and two-compartment models with proportional noise; no multi-subject files,
  no wrong-unit CSV headers, no data error.
