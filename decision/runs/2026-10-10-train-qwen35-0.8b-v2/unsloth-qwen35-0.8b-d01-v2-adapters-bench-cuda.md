# qwen35-0.8b-d01-v2-adapters on bench (Unsloth decision model)

`decision/predict_unsloth.py`, `FastDecisionModel.predict`, one call per row. Gold is one-hot, so calibration is measured against a certain label; `noul` probabilities are P(true). Python 3.12.10, torch 2.14.1+cu130.

| run | rows | overall accuracy | ECE | ms per row | device/dtype |
|---|---|---|---|---|---|
| qwen35-0.8b-d01-v2-adapters, bench | 1150 | 100.0 % | 0.000 | 206.7 | cuda/bfloat16 |

## qwen35-0.8b-d01-v2-adapters, bench

Rows 1150, questions 23000, device cuda, dtype bfloat16, model load 23.6 s, inference wall 237.9 s (after 2 untimed warm-up rows).
Time per row (one call, 20 questions): mean 206.7 ms, median 206.9 ms, p95 209.7 ms. VRAM: nvidia-smi used 686 MiB before load, 2325 after the run; torch peak allocated 1441 MiB.

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 1150 | 1150 | 100.0 % | 45.7 % | 0.000 |
| asked_adj_r2 | 1150 | 1150 | 100.0 % | 94.4 % | 0.000 |
| asked_aucinf | 1150 | 1150 | 100.0 % | 90.0 % | 0.000 |
| asked_auclast | 1150 | 1150 | 100.0 % | 82.2 % | 0.000 |
| asked_aucpext | 1150 | 1150 | 100.0 % | 94.3 % | 0.000 |
| asked_c0 | 1150 | 1150 | 100.0 % | 95.0 % | 0.000 |
| asked_cl | 1150 | 1150 | 100.0 % | 88.8 % | 0.000 |
| asked_cmax | 1150 | 1150 | 100.0 % | 86.6 % | 0.000 |
| asked_half_life | 1150 | 1150 | 100.0 % | 87.1 % | 0.000 |
| asked_lambda_z | 1150 | 1150 | 100.0 % | 92.5 % | 0.000 |
| asked_lambda_z_points | 1150 | 1150 | 100.0 % | 95.6 % | 0.000 |
| asked_mrt | 1150 | 1150 | 100.0 % | 92.0 % | 0.000 |
| asked_tlag | 1150 | 1150 | 100.0 % | 97.0 % | 0.000 |
| asked_tmax | 1150 | 1150 | 100.0 % | 88.0 % | 0.000 |
| asked_vz | 1150 | 1150 | 100.0 % | 89.6 % | 0.000 |
| auc_method | 1143 | 1150 | 99.4 % | 78.3 % | 0.004 |
| compare_pair | 1150 | 1150 | 100.0 % | 87.0 % | 0.002 |
| dose_has_unit | 1150 | 1150 | 100.0 % | 82.0 % | 0.000 |
| is_not_available | 1149 | 1150 | 99.9 % | 93.5 % | 0.002 |
| route | 1150 | 1150 | 100.0 % | 47.6 % | 0.000 |
| **overall** | 22992 | 23000 | **100.0 %** | 85.3 % | 0.000 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | not_supported | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|---|
| compare | 150 |  |  |  |  |  |  | 150 | 100.0 % |
| fit_pk1 |  | 75 |  |  |  |  |  | 75 | 100.0 % |
| fit_pk2 |  |  | 75 |  |  |  |  | 75 | 100.0 % |
| nca |  |  |  | 175 |  |  |  | 175 | 100.0 % |
| none_needed |  |  |  |  | 525 |  |  | 525 | 100.0 % |
| not_supported |  |  |  |  |  | 75 |  | 75 | 100.0 % |
| simulate |  |  |  |  |  |  | 75 | 75 | 100.0 % |

### Confusion: route (rows = gold, columns = predicted)

| gold \ pred | iv_bolus | iv_infusion | oral | unknown | total | recall |
|---|---|---|---|---|---|---|
| iv_bolus | 313 |  |  |  | 313 | 100.0 % |
| iv_infusion |  | 117 |  |  | 117 | 100.0 % |
| oral |  |  | 547 |  | 547 | 100.0 % |
| unknown |  |  |  | 173 | 173 | 100.0 % |

### Confusion: auc_method (rows = gold, columns = predicted)

| gold \ pred | lin_up_log_down | linear | not_applicable | total | recall |
|---|---|---|---|---|---|
| lin_up_log_down | 94 |  |  | 94 | 100.0 % |
| linear |  | 149 | 7 | 156 | 95.5 % |
| not_applicable |  |  | 900 | 900 | 100.0 % |

### Confusion: compare_pair (rows = gold, columns = predicted)

| gold \ pred | 2+3 | 3+2 | not_applicable | total | recall |
|---|---|---|---|---|---|
| 2+3 | 113 |  |  | 113 | 100.0 % |
| 3+2 |  | 37 |  | 37 | 100.0 % |
| not_applicable |  |  | 1000 | 1000 | 100.0 % |

### Confusion: is_not_available (rows = gold, columns = predicted)

| gold \ pred | false | true | total | recall |
|---|---|---|---|---|
| false | 1075 |  | 1075 | 100.0 % |
| true | 1 | 74 | 75 | 98.7 % |

### Calibration (all questions; probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 0 | - | - |
| [0.3, 0.4) | 0 | - | - |
| [0.4, 0.5) | 0 | - | - |
| [0.5, 0.6) | 1 | 0.589 | 0.000 |
| [0.6, 0.7) | 3 | 0.650 | 0.667 |
| [0.7, 0.8) | 8 | 0.768 | 0.875 |
| [0.8, 0.9) | 13 | 0.850 | 0.846 |
| [0.9, 1.0] | 22975 | 1.000 | 1.000 |

Expected calibration error: 0.000.

### Questions at or below the always-majority baseline

None: every question is above its baseline.

