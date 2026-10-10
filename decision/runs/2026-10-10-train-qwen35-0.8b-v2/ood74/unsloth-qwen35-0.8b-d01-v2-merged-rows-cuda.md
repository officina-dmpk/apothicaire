# qwen35-0.8b-d01-v2-merged on rows (Unsloth decision model)

`decision/predict_unsloth.py`, `FastDecisionModel.predict`, one call per row. Gold is one-hot, so calibration is measured against a certain label; `noul` probabilities are P(true). Python 3.12.10, torch 2.14.1+cu130.

| run | rows | overall accuracy | ECE | ms per row | device/dtype |
|---|---|---|---|---|---|
| qwen35-0.8b-d01-v2-merged, rows | 74 | 94.1 % | 0.054 | 174.0 | cuda/bfloat16 |

## qwen35-0.8b-d01-v2-merged, rows

Rows 74, questions 1480, device cuda, dtype bfloat16, model load 21.8 s, inference wall 12.9 s (after 2 untimed warm-up rows).
Time per row (one call, 20 questions): mean 174.0 ms, median 174.6 ms, p95 178.1 ms. VRAM: nvidia-smi used 686 MiB before load, 2807 after the run; torch peak allocated 1938 MiB.

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 61 | 74 | 82.4 % | 60.8 % | 0.142 |
| asked_adj_r2 | 74 | 74 | 100.0 % | 98.6 % | 0.000 |
| asked_aucinf | 67 | 74 | 90.5 % | 91.9 % | 0.093 |
| asked_auclast | 67 | 74 | 90.5 % | 73.0 % | 0.092 |
| asked_aucpext | 72 | 74 | 97.3 % | 95.9 % | 0.027 |
| asked_c0 | 74 | 74 | 100.0 % | 95.9 % | 0.000 |
| asked_cl | 73 | 74 | 98.6 % | 87.8 % | 0.014 |
| asked_cmax | 73 | 74 | 98.6 % | 70.3 % | 0.013 |
| asked_half_life | 74 | 74 | 100.0 % | 87.8 % | 0.000 |
| asked_lambda_z | 74 | 74 | 100.0 % | 98.6 % | 0.000 |
| asked_lambda_z_points | 74 | 74 | 100.0 % | 97.3 % | 0.000 |
| asked_mrt | 74 | 74 | 100.0 % | 95.9 % | 0.000 |
| asked_tlag | 74 | 74 | 100.0 % | 94.6 % | 0.000 |
| asked_tmax | 74 | 74 | 100.0 % | 90.5 % | 0.000 |
| asked_vz | 73 | 74 | 98.6 % | 87.8 % | 0.014 |
| auc_method | 40 | 74 | 54.1 % | 77.0 % | 0.433 |
| compare_pair | 72 | 74 | 97.3 % | 94.6 % | 0.022 |
| dose_has_unit | 72 | 74 | 97.3 % | 93.2 % | 0.026 |
| is_not_available | 63 | 74 | 85.1 % | 85.1 % | 0.149 |
| route | 67 | 74 | 90.5 % | 54.1 % | 0.089 |
| **overall** | 1392 | 1480 | **94.1 %** | 86.6 % | 0.054 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | not_supported | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|---|
| compare | 8 |  |  |  |  |  |  | 8 | 100.0 % |
| fit_pk1 |  | 1 |  |  |  |  |  | 1 | 100.0 % |
| fit_pk2 |  |  | 3 |  |  |  |  | 3 | 100.0 % |
| nca |  |  |  | 38 | 6 | 1 |  | 45 | 84.4 % |
| none_needed |  |  |  | 3 | 11 | 2 |  | 16 | 68.8 % |
| simulate |  |  |  | 1 |  |  |  | 1 | 0.0 % |

### Confusion: route (rows = gold, columns = predicted)

| gold \ pred | iv_bolus | iv_infusion | oral | unknown | total | recall |
|---|---|---|---|---|---|---|
| iv_bolus | 20 | 1 |  | 1 | 22 | 90.9 % |
| iv_infusion |  | 10 |  |  | 10 | 100.0 % |
| oral |  |  | 35 | 5 | 40 | 87.5 % |
| unknown |  |  |  | 2 | 2 | 100.0 % |

### Confusion: auc_method (rows = gold, columns = predicted)

| gold \ pred | lin_up_log_down | linear | not_applicable | total | recall |
|---|---|---|---|---|---|
| lin_up_log_down | 6 |  | 2 | 8 | 75.0 % |
| linear |  | 25 | 32 | 57 | 43.9 % |
| not_applicable |  |  | 9 | 9 | 100.0 % |

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
| [0.5, 0.6) | 4 | 0.561 | 0.250 |
| [0.6, 0.7) | 9 | 0.649 | 0.111 |
| [0.7, 0.8) | 6 | 0.755 | 0.333 |
| [0.8, 0.9) | 4 | 0.858 | 0.500 |
| [0.9, 1.0] | 1457 | 0.999 | 0.951 |

Expected calibration error: 0.054.

### Questions at or below the always-majority baseline

| question | accuracy | always-majority | difference (points) |
|---|---|---|---|
| auc_method | 54.1 % | 77.0 % | -23.0 |
| asked_aucinf | 90.5 % | 91.9 % | -1.4 |
| is_not_available | 85.1 % | 85.1 % | +0.0 |

