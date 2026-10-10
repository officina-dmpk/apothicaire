# qwen35-0.8b-d01-v2-merged on bench (Unsloth decision model)

`decision/predict_unsloth.py`, `FastDecisionModel.predict`, one call per row. Gold is one-hot, so calibration is measured against a certain label; `noul` probabilities are P(true). Python 3.12.10, torch 2.14.1+cu130.

| run | rows | overall accuracy | ECE | ms per row | device/dtype |
|---|---|---|---|---|---|
| qwen35-0.8b-d01-v2-merged, bench | 1150 | 99.5 % | 0.004 | 177.9 | cuda/bfloat16 |

## qwen35-0.8b-d01-v2-merged, bench

Rows 1150, questions 23000, device cuda, dtype bfloat16, model load 22.6 s, inference wall 204.7 s (after 2 untimed warm-up rows).
Time per row (one call, 20 questions): mean 177.9 ms, median 178.0 ms, p95 180.6 ms. VRAM: nvidia-smi used 686 MiB before load, 2807 after the run; torch peak allocated 1942 MiB.

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 1136 | 1150 | 98.8 % | 45.7 % | 0.007 |
| asked_adj_r2 | 1150 | 1150 | 100.0 % | 94.4 % | 0.000 |
| asked_aucinf | 1150 | 1150 | 100.0 % | 90.0 % | 0.000 |
| asked_auclast | 1150 | 1150 | 100.0 % | 82.2 % | 0.000 |
| asked_aucpext | 1150 | 1150 | 100.0 % | 94.3 % | 0.000 |
| asked_c0 | 1150 | 1150 | 100.0 % | 95.0 % | 0.000 |
| asked_cl | 1150 | 1150 | 100.0 % | 88.8 % | 0.001 |
| asked_cmax | 1150 | 1150 | 100.0 % | 86.6 % | 0.000 |
| asked_half_life | 1150 | 1150 | 100.0 % | 87.1 % | 0.000 |
| asked_lambda_z | 1150 | 1150 | 100.0 % | 92.5 % | 0.001 |
| asked_lambda_z_points | 1150 | 1150 | 100.0 % | 95.6 % | 0.000 |
| asked_mrt | 1150 | 1150 | 100.0 % | 92.0 % | 0.000 |
| asked_tlag | 1150 | 1150 | 100.0 % | 97.0 % | 0.000 |
| asked_tmax | 1150 | 1150 | 100.0 % | 88.0 % | 0.000 |
| asked_vz | 1150 | 1150 | 100.0 % | 89.6 % | 0.000 |
| auc_method | 1129 | 1150 | 98.2 % | 78.3 % | 0.013 |
| compare_pair | 1143 | 1150 | 99.4 % | 87.0 % | 0.006 |
| dose_has_unit | 1147 | 1150 | 99.7 % | 82.0 % | 0.003 |
| is_not_available | 1075 | 1150 | 93.5 % | 93.5 % | 0.065 |
| route | 1150 | 1150 | 100.0 % | 47.6 % | 0.000 |
| **overall** | 22880 | 23000 | **99.5 %** | 85.3 % | 0.004 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | not_supported | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|---|
| compare | 150 |  |  |  |  |  |  | 150 | 100.0 % |
| fit_pk1 |  | 68 |  | 2 | 5 |  |  | 75 | 90.7 % |
| fit_pk2 |  |  | 75 |  |  |  |  | 75 | 100.0 % |
| nca |  |  |  | 174 | 1 |  |  | 175 | 99.4 % |
| none_needed |  |  |  |  | 525 |  |  | 525 | 100.0 % |
| not_supported |  |  |  | 2 | 4 | 69 |  | 75 | 92.0 % |
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
| linear |  | 142 | 14 | 156 | 91.0 % |
| not_applicable | 7 |  | 893 | 900 | 99.2 % |

### Confusion: compare_pair (rows = gold, columns = predicted)

| gold \ pred | 2+3 | 3+2 | not_applicable | total | recall |
|---|---|---|---|---|---|
| 2+3 | 113 |  |  | 113 | 100.0 % |
| 3+2 | 7 | 30 |  | 37 | 81.1 % |
| not_applicable |  |  | 1000 | 1000 | 100.0 % |

### Confusion: is_not_available (rows = gold, columns = predicted)

| gold \ pred | false | true | total | recall |
|---|---|---|---|---|
| false | 1075 |  | 1075 | 100.0 % |
| true | 75 |  | 75 | 0.0 % |

### Calibration (all questions; probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 0 | - | - |
| [0.3, 0.4) | 0 | - | - |
| [0.4, 0.5) | 1 | 0.475 | 0.000 |
| [0.5, 0.6) | 8 | 0.563 | 0.500 |
| [0.6, 0.7) | 10 | 0.654 | 0.500 |
| [0.7, 0.8) | 22 | 0.754 | 0.727 |
| [0.8, 0.9) | 45 | 0.861 | 0.867 |
| [0.9, 1.0] | 22914 | 1.000 | 0.996 |

Expected calibration error: 0.004.

### Questions at or below the always-majority baseline

| question | accuracy | always-majority | difference (points) |
|---|---|---|---|
| is_not_available | 93.5 % | 93.5 % | +0.0 |

