# qwen35-0.8b-d01-v2-adapters on heldout_exercises (Unsloth decision model)

`decision/predict_unsloth.py`, `FastDecisionModel.predict`, one call per row. Gold is one-hot, so calibration is measured against a certain label; `noul` probabilities are P(true). Python 3.12.10, torch 2.14.1+cu130.

| run | rows | overall accuracy | ECE | ms per row | device/dtype |
|---|---|---|---|---|---|
| qwen35-0.8b-d01-v2-adapters, heldout_exercises (every 4th) | 230 | 100.0 % | 0.000 | 205.9 | cuda/bfloat16 |

## qwen35-0.8b-d01-v2-adapters, heldout_exercises (every 4th)

Rows 230, questions 4600, device cuda, dtype bfloat16, model load 23.8 s, inference wall 47.4 s (after 2 untimed warm-up rows).
Time per row (one call, 20 questions): mean 205.9 ms, median 205.6 ms, p95 208.5 ms. VRAM: nvidia-smi used 686 MiB before load, 2309 after the run; torch peak allocated 1436 MiB.

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 230 | 230 | 100.0 % | 47.8 % | 0.000 |
| asked_adj_r2 | 230 | 230 | 100.0 % | 95.7 % | 0.000 |
| asked_aucinf | 230 | 230 | 100.0 % | 93.9 % | 0.000 |
| asked_auclast | 230 | 230 | 100.0 % | 83.9 % | 0.000 |
| asked_aucpext | 230 | 230 | 100.0 % | 94.3 % | 0.000 |
| asked_c0 | 230 | 230 | 100.0 % | 94.8 % | 0.000 |
| asked_cl | 230 | 230 | 100.0 % | 89.6 % | 0.000 |
| asked_cmax | 230 | 230 | 100.0 % | 88.3 % | 0.000 |
| asked_half_life | 230 | 230 | 100.0 % | 86.1 % | 0.000 |
| asked_lambda_z | 230 | 230 | 100.0 % | 96.1 % | 0.000 |
| asked_lambda_z_points | 230 | 230 | 100.0 % | 95.2 % | 0.000 |
| asked_mrt | 230 | 230 | 100.0 % | 92.6 % | 0.000 |
| asked_tlag | 230 | 230 | 100.0 % | 97.0 % | 0.000 |
| asked_tmax | 230 | 230 | 100.0 % | 87.4 % | 0.000 |
| asked_vz | 230 | 230 | 100.0 % | 87.8 % | 0.000 |
| auc_method | 229 | 230 | 99.6 % | 80.9 % | 0.004 |
| compare_pair | 230 | 230 | 100.0 % | 88.3 % | 0.001 |
| dose_has_unit | 230 | 230 | 100.0 % | 83.5 % | 0.000 |
| is_not_available | 230 | 230 | 100.0 % | 93.9 % | 0.003 |
| route | 230 | 230 | 100.0 % | 45.2 % | 0.000 |
| **overall** | 4599 | 4600 | **100.0 %** | 86.1 % | 0.000 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | not_supported | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|---|
| compare | 27 |  |  |  |  |  |  | 27 | 100.0 % |
| fit_pk1 |  | 14 |  |  |  |  |  | 14 | 100.0 % |
| fit_pk2 |  |  | 18 |  |  |  |  | 18 | 100.0 % |
| nca |  |  |  | 33 |  |  |  | 33 | 100.0 % |
| none_needed |  |  |  |  | 110 |  |  | 110 | 100.0 % |
| not_supported |  |  |  |  |  | 13 |  | 13 | 100.0 % |
| simulate |  |  |  |  |  |  | 15 | 15 | 100.0 % |

### Confusion: route (rows = gold, columns = predicted)

| gold \ pred | iv_bolus | iv_infusion | oral | unknown | total | recall |
|---|---|---|---|---|---|---|
| iv_bolus | 74 |  |  |  | 74 | 100.0 % |
| iv_infusion |  | 33 |  |  | 33 | 100.0 % |
| oral |  |  | 104 |  | 104 | 100.0 % |
| unknown |  |  |  | 19 | 19 | 100.0 % |

### Confusion: auc_method (rows = gold, columns = predicted)

| gold \ pred | lin_up_log_down | linear | not_applicable | total | recall |
|---|---|---|---|---|---|
| lin_up_log_down | 15 |  |  | 15 | 100.0 % |
| linear |  | 28 | 1 | 29 | 96.6 % |
| not_applicable |  |  | 186 | 186 | 100.0 % |

### Confusion: compare_pair (rows = gold, columns = predicted)

| gold \ pred | 2+3 | 3+2 | not_applicable | total | recall |
|---|---|---|---|---|---|
| 2+3 | 20 |  |  | 20 | 100.0 % |
| 3+2 |  | 7 |  | 7 | 100.0 % |
| not_applicable |  |  | 203 | 203 | 100.0 % |

### Confusion: is_not_available (rows = gold, columns = predicted)

| gold \ pred | false | true | total | recall |
|---|---|---|---|---|
| false | 216 |  | 216 | 100.0 % |
| true |  | 14 | 14 | 100.0 % |

### Calibration (all questions; probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 0 | - | - |
| [0.3, 0.4) | 0 | - | - |
| [0.4, 0.5) | 0 | - | - |
| [0.5, 0.6) | 0 | - | - |
| [0.6, 0.7) | 0 | - | - |
| [0.7, 0.8) | 1 | 0.720 | 1.000 |
| [0.8, 0.9) | 3 | 0.863 | 1.000 |
| [0.9, 1.0] | 4596 | 1.000 | 1.000 |

Expected calibration error: 0.000.

### Questions at or below the always-majority baseline

None: every question is above its baseline.

