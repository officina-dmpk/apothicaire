# qwen35-0.8b-d01-v2-adapters on rows (Unsloth decision model)

`decision/predict_unsloth.py`, `FastDecisionModel.predict`, one call per row. Gold is one-hot, so calibration is measured against a certain label; `noul` probabilities are P(true). Python 3.12.10, torch 2.14.1+cu130.

| run | rows | overall accuracy | ECE | ms per row | device/dtype |
|---|---|---|---|---|---|
| qwen35-0.8b-d01-v2-adapters, rows | 74 | 93.9 % | 0.057 | 202.8 | cuda/bfloat16 |

## qwen35-0.8b-d01-v2-adapters, rows

Rows 74, questions 1480, device cuda, dtype bfloat16, model load 23.4 s, inference wall 15.0 s (after 2 untimed warm-up rows).
Time per row (one call, 20 questions): mean 202.8 ms, median 203.1 ms, p95 207.7 ms. VRAM: nvidia-smi used 686 MiB before load, 2325 after the run; torch peak allocated 1437 MiB.

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 55 | 74 | 74.3 % | 60.8 % | 0.229 |
| asked_adj_r2 | 74 | 74 | 100.0 % | 98.6 % | 0.000 |
| asked_aucinf | 67 | 74 | 90.5 % | 91.9 % | 0.088 |
| asked_auclast | 67 | 74 | 90.5 % | 73.0 % | 0.092 |
| asked_aucpext | 72 | 74 | 97.3 % | 95.9 % | 0.027 |
| asked_c0 | 74 | 74 | 100.0 % | 95.9 % | 0.000 |
| asked_cl | 73 | 74 | 98.6 % | 87.8 % | 0.014 |
| asked_cmax | 73 | 74 | 98.6 % | 70.3 % | 0.014 |
| asked_half_life | 74 | 74 | 100.0 % | 87.8 % | 0.000 |
| asked_lambda_z | 74 | 74 | 100.0 % | 98.6 % | 0.000 |
| asked_lambda_z_points | 74 | 74 | 100.0 % | 97.3 % | 0.000 |
| asked_mrt | 74 | 74 | 100.0 % | 95.9 % | 0.000 |
| asked_tlag | 74 | 74 | 100.0 % | 94.6 % | 0.000 |
| asked_tmax | 74 | 74 | 100.0 % | 90.5 % | 0.000 |
| asked_vz | 73 | 74 | 98.6 % | 87.8 % | 0.014 |
| auc_method | 50 | 74 | 67.6 % | 77.0 % | 0.307 |
| compare_pair | 72 | 74 | 97.3 % | 94.6 % | 0.025 |
| dose_has_unit | 72 | 74 | 97.3 % | 93.2 % | 0.027 |
| is_not_available | 63 | 74 | 85.1 % | 85.1 % | 0.148 |
| route | 60 | 74 | 81.1 % | 54.1 % | 0.181 |
| **overall** | 1389 | 1480 | **93.9 %** | 86.6 % | 0.057 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | not_supported | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|---|
| compare | 8 |  |  |  |  |  |  | 8 | 100.0 % |
| fit_pk1 |  | 1 |  |  |  |  |  | 1 | 100.0 % |
| fit_pk2 |  |  | 3 |  |  |  |  | 3 | 100.0 % |
| nca |  |  |  | 31 | 14 |  |  | 45 | 68.9 % |
| none_needed |  |  |  | 1 | 11 | 4 |  | 16 | 68.8 % |
| simulate |  |  |  |  |  |  | 1 | 1 | 100.0 % |

### Confusion: route (rows = gold, columns = predicted)

| gold \ pred | iv_bolus | iv_infusion | oral | unknown | total | recall |
|---|---|---|---|---|---|---|
| iv_bolus | 19 | 1 |  | 2 | 22 | 86.4 % |
| iv_infusion |  | 5 |  | 5 | 10 | 50.0 % |
| oral |  |  | 34 | 6 | 40 | 85.0 % |
| unknown |  |  |  | 2 | 2 | 100.0 % |

### Confusion: auc_method (rows = gold, columns = predicted)

| gold \ pred | lin_up_log_down | linear | not_applicable | total | recall |
|---|---|---|---|---|---|
| lin_up_log_down | 6 |  | 2 | 8 | 75.0 % |
| linear |  | 36 | 21 | 57 | 63.2 % |
| not_applicable |  | 1 | 8 | 9 | 88.9 % |

### Confusion: compare_pair (rows = gold, columns = predicted)

| gold \ pred | 2+3 | 3+2 | not_applicable | total | recall |
|---|---|---|---|---|---|
| 2+3 | 2 |  |  | 2 | 100.0 % |
| 3+2 | 2 |  |  | 2 | 0.0 % |
| not_applicable |  |  | 70 | 70 | 100.0 % |

### Confusion: is_not_available (rows = gold, columns = predicted)

| gold \ pred | false | true | total | recall |
|---|---|---|---|---|
| false | 63 |  | 63 | 100.0 % |
| true | 11 |  | 11 | 0.0 % |

### Calibration (all questions; probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 0 | - | - |
| [0.3, 0.4) | 0 | - | - |
| [0.4, 0.5) | 0 | - | - |
| [0.5, 0.6) | 7 | 0.557 | 0.429 |
| [0.6, 0.7) | 2 | 0.675 | 0.000 |
| [0.7, 0.8) | 5 | 0.731 | 0.000 |
| [0.8, 0.9) | 5 | 0.862 | 0.400 |
| [0.9, 1.0] | 1461 | 0.999 | 0.947 |

Expected calibration error: 0.057.

### Questions at or below the always-majority baseline

| question | accuracy | always-majority | difference (points) |
|---|---|---|---|
| auc_method | 67.6 % | 77.0 % | -9.5 |
| asked_aucinf | 90.5 % | 91.9 % | -1.4 |
| is_not_available | 85.1 % | 85.1 % | +0.0 |

