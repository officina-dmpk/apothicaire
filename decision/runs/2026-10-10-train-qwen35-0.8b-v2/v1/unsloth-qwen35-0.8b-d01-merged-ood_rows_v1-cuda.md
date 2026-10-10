# qwen35-0.8b-d01-merged on ood_rows_v1 (Unsloth decision model)

`decision/predict_unsloth.py`, `FastDecisionModel.predict`, one call per row. Gold is one-hot, so calibration is measured against a certain label; `noul` probabilities are P(true). Python 3.12.10, torch 2.14.1+cu130.

| run | rows | overall accuracy | ECE | ms per row | device/dtype |
|---|---|---|---|---|---|
| qwen35-0.8b-d01-merged, ood_rows_v1 | 74 | 90.3 % | 0.094 | 167.9 | cuda/bfloat16 |

## qwen35-0.8b-d01-merged, ood_rows_v1

Rows 74, questions 1480, device cuda, dtype bfloat16, model load 21.7 s, inference wall 12.4 s (after 2 untimed warm-up rows).
Time per row (one call, 20 questions): mean 167.9 ms, median 167.4 ms, p95 169.1 ms. VRAM: nvidia-smi used 686 MiB before load, 2853 after the run; torch peak allocated 1935 MiB.

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 28 | 74 | 37.8 % | 60.8 % | 0.614 |
| asked_adj_r2 | 74 | 74 | 100.0 % | 98.6 % | 0.000 |
| asked_aucinf | 69 | 74 | 93.2 % | 91.9 % | 0.043 |
| asked_auclast | 68 | 74 | 91.9 % | 73.0 % | 0.087 |
| asked_aucpext | 74 | 74 | 100.0 % | 95.9 % | 0.000 |
| asked_c0 | 74 | 74 | 100.0 % | 95.9 % | 0.000 |
| asked_cl | 73 | 74 | 98.6 % | 87.8 % | 0.013 |
| asked_cmax | 73 | 74 | 98.6 % | 70.3 % | 0.013 |
| asked_half_life | 74 | 74 | 100.0 % | 87.8 % | 0.000 |
| asked_lambda_z | 74 | 74 | 100.0 % | 98.6 % | 0.000 |
| asked_lambda_z_points | 74 | 74 | 100.0 % | 97.3 % | 0.000 |
| asked_mrt | 74 | 74 | 100.0 % | 95.9 % | 0.000 |
| asked_tlag | 74 | 74 | 100.0 % | 94.6 % | 0.000 |
| asked_tmax | 74 | 74 | 100.0 % | 90.5 % | 0.000 |
| asked_vz | 73 | 74 | 98.6 % | 87.8 % | 0.013 |
| auc_method | 16 | 74 | 21.6 % | 77.0 % | 0.776 |
| compare_pair | 74 | 74 | 100.0 % | 94.6 % | 0.000 |
| dose_has_unit | 73 | 74 | 98.6 % | 93.2 % | 0.013 |
| is_not_available | 63 | 74 | 85.1 % | 85.1 % | 0.148 |
| route | 61 | 74 | 82.4 % | 54.1 % | 0.180 |
| **overall** | 1337 | 1480 | **90.3 %** | 86.6 % | 0.094 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|
| compare | 8 |  |  |  |  |  | 8 | 100.0 % |
| fit_pk1 |  | 1 |  |  |  |  | 1 | 100.0 % |
| fit_pk2 |  |  | 3 |  |  |  | 3 | 100.0 % |
| nca |  |  |  |  | 45 |  | 45 | 0.0 % |
| none_needed |  |  |  |  | 16 |  | 16 | 100.0 % |
| simulate |  |  |  |  | 1 |  | 1 | 0.0 % |

### Confusion: route (rows = gold, columns = predicted)

| gold \ pred | iv_bolus | iv_infusion | oral | unknown | total | recall |
|---|---|---|---|---|---|---|
| iv_bolus | 22 |  |  |  | 22 | 100.0 % |
| iv_infusion |  | 3 |  | 7 | 10 | 30.0 % |
| oral |  |  | 34 | 6 | 40 | 85.0 % |
| unknown |  |  |  | 2 | 2 | 100.0 % |

### Confusion: auc_method (rows = gold, columns = predicted)

| gold \ pred | lin_up_log_down | linear | not_applicable | total | recall |
|---|---|---|---|---|---|
| lin_up_log_down | 6 |  | 2 | 8 | 75.0 % |
| linear |  | 1 | 56 | 57 | 1.8 % |
| not_applicable |  |  | 9 | 9 | 100.0 % |

### Confusion: compare_pair (rows = gold, columns = predicted)

| gold \ pred | 2+3 | not_applicable | total | recall |
|---|---|---|---|---|
| 2+3 | 4 |  | 4 | 100.0 % |
| not_applicable |  | 70 | 70 | 100.0 % |

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
| [0.5, 0.6) | 5 | 0.566 | 0.200 |
| [0.6, 0.7) | 4 | 0.676 | 0.500 |
| [0.7, 0.8) | 2 | 0.762 | 1.000 |
| [0.8, 0.9) | 4 | 0.858 | 0.500 |
| [0.9, 1.0] | 1465 | 0.999 | 0.908 |

Expected calibration error: 0.094.

### Questions at or below the always-majority baseline

| question | accuracy | always-majority | difference (points) |
|---|---|---|---|
| auc_method | 21.6 % | 77.0 % | -55.4 |
| analysis | 37.8 % | 60.8 % | -23.0 |
| is_not_available | 85.1 % | 85.1 % | +0.0 |

