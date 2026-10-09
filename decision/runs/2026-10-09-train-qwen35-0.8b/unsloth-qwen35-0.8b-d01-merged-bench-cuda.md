# qwen35-0.8b-d01-merged on bench (Unsloth decision model)

`decision/predict_unsloth.py`, `FastDecisionModel.predict`, one call per row. Gold is one-hot, so calibration is measured against a certain label; `noul` probabilities are P(true). Python 3.12.10, torch 2.14.1+cu130.

| run | rows | overall accuracy | ECE | ms per row | device/dtype |
|---|---|---|---|---|---|
| qwen35-0.8b-d01-merged, bench | 900 | 99.9 % | 0.001 | 175.5 | cuda/bfloat16 |

## qwen35-0.8b-d01-merged, bench

Rows 900, questions 18000, device cuda, dtype bfloat16, model load 23.2 s, inference wall 158.1 s (after 2 untimed warm-up rows).
Time per row (one call, 20 questions): mean 175.5 ms, median 176.8 ms, p95 178.6 ms. VRAM: nvidia-smi used 700 MiB before load, 2867 after the run; torch peak allocated 1936 MiB.

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 900 | 900 | 100.0 % | 58.3 % | 0.005 |
| asked_adj_r2 | 900 | 900 | 100.0 % | 93.8 % | 0.000 |
| asked_aucinf | 900 | 900 | 100.0 % | 87.6 % | 0.000 |
| asked_auclast | 900 | 900 | 100.0 % | 81.8 % | 0.000 |
| asked_aucpext | 900 | 900 | 100.0 % | 94.2 % | 0.000 |
| asked_c0 | 900 | 900 | 100.0 % | 92.9 % | 0.000 |
| asked_cl | 900 | 900 | 100.0 % | 84.4 % | 0.000 |
| asked_cmax | 900 | 900 | 100.0 % | 84.1 % | 0.000 |
| asked_half_life | 900 | 900 | 100.0 % | 84.3 % | 0.000 |
| asked_lambda_z | 900 | 900 | 100.0 % | 90.2 % | 0.000 |
| asked_lambda_z_points | 900 | 900 | 100.0 % | 93.0 % | 0.000 |
| asked_mrt | 900 | 900 | 100.0 % | 88.7 % | 0.000 |
| asked_tlag | 900 | 900 | 100.0 % | 96.9 % | 0.000 |
| asked_tmax | 900 | 900 | 100.0 % | 84.4 % | 0.000 |
| asked_vz | 900 | 900 | 100.0 % | 84.8 % | 0.000 |
| auc_method | 900 | 900 | 100.0 % | 83.3 % | 0.001 |
| compare_pair | 900 | 900 | 100.0 % | 91.7 % | 0.000 |
| dose_has_unit | 900 | 900 | 100.0 % | 84.0 % | 0.000 |
| is_not_available | 882 | 900 | 98.0 % | 91.7 % | 0.015 |
| route | 900 | 900 | 100.0 % | 49.8 % | 0.000 |
| **overall** | 17982 | 18000 | **99.9 %** | 85.0 % | 0.001 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|
| compare | 75 |  |  |  |  |  | 75 | 100.0 % |
| fit_pk1 |  | 75 |  |  |  |  | 75 | 100.0 % |
| fit_pk2 |  |  | 75 |  |  |  | 75 | 100.0 % |
| nca |  |  |  | 75 |  |  | 75 | 100.0 % |
| none_needed |  |  |  |  | 525 |  | 525 | 100.0 % |
| simulate |  |  |  |  |  | 75 | 75 | 100.0 % |

### Confusion: route (rows = gold, columns = predicted)

| gold \ pred | iv_bolus | iv_infusion | oral | unknown | total | recall |
|---|---|---|---|---|---|---|
| iv_bolus | 241 |  |  |  | 241 | 100.0 % |
| iv_infusion |  | 95 |  |  | 95 | 100.0 % |
| oral |  |  | 448 |  | 448 | 100.0 % |
| unknown |  |  |  | 116 | 116 | 100.0 % |

### Confusion: auc_method (rows = gold, columns = predicted)

| gold \ pred | lin_up_log_down | linear | not_applicable | total | recall |
|---|---|---|---|---|---|
| lin_up_log_down | 75 |  |  | 75 | 100.0 % |
| linear |  | 75 |  | 75 | 100.0 % |
| not_applicable |  |  | 750 | 750 | 100.0 % |

### Confusion: compare_pair (rows = gold, columns = predicted)

| gold \ pred | 2+3 | not_applicable | total | recall |
|---|---|---|---|---|
| 2+3 | 75 |  | 75 | 100.0 % |
| not_applicable |  | 825 | 825 | 100.0 % |

### Confusion: is_not_available (rows = gold, columns = predicted)

| gold \ pred | false | true | total | recall |
|---|---|---|---|---|
| false | 824 | 1 | 825 | 99.9 % |
| true | 17 | 58 | 75 | 77.3 % |

### Calibration (all questions; probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 0 | - | - |
| [0.3, 0.4) | 0 | - | - |
| [0.4, 0.5) | 0 | - | - |
| [0.5, 0.6) | 18 | 0.544 | 0.667 |
| [0.6, 0.7) | 23 | 0.646 | 0.565 |
| [0.7, 0.8) | 24 | 0.758 | 1.000 |
| [0.8, 0.9) | 26 | 0.853 | 0.923 |
| [0.9, 1.0] | 17909 | 1.000 | 1.000 |

Expected calibration error: 0.001.

### Questions at or below the always-majority baseline

None: every question is above its baseline.

