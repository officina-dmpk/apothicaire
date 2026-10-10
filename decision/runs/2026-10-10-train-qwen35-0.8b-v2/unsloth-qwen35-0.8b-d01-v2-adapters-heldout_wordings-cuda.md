# qwen35-0.8b-d01-v2-adapters on heldout_wordings (Unsloth decision model)

`decision/predict_unsloth.py`, `FastDecisionModel.predict`, one call per row. Gold is one-hot, so calibration is measured against a certain label; `noul` probabilities are P(true). Python 3.12.10, torch 2.14.1+cu130.

| run | rows | overall accuracy | ECE | ms per row | device/dtype |
|---|---|---|---|---|---|
| qwen35-0.8b-d01-v2-adapters, heldout_wordings | 825 | 98.2 % | 0.016 | 206.8 | cuda/bfloat16 |

## qwen35-0.8b-d01-v2-adapters, heldout_wordings

Rows 825, questions 16500, device cuda, dtype bfloat16, model load 23.7 s, inference wall 170.7 s (after 2 untimed warm-up rows).
Time per row (one call, 20 questions): mean 206.8 ms, median 206.9 ms, p95 209.6 ms. VRAM: nvidia-smi used 686 MiB before load, 2325 after the run; torch peak allocated 1446 MiB.

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 785 | 825 | 95.2 % | 46.7 % | 0.032 |
| asked_adj_r2 | 825 | 825 | 100.0 % | 93.9 % | 0.000 |
| asked_aucinf | 823 | 825 | 99.8 % | 88.5 % | 0.003 |
| asked_auclast | 798 | 825 | 96.7 % | 84.6 % | 0.031 |
| asked_aucpext | 825 | 825 | 100.0 % | 96.2 % | 0.000 |
| asked_c0 | 825 | 825 | 100.0 % | 95.6 % | 0.000 |
| asked_cl | 812 | 825 | 98.4 % | 92.8 % | 0.015 |
| asked_cmax | 802 | 825 | 97.2 % | 84.4 % | 0.028 |
| asked_half_life | 825 | 825 | 100.0 % | 82.7 % | 0.000 |
| asked_lambda_z | 813 | 825 | 98.5 % | 95.2 % | 0.014 |
| asked_lambda_z_points | 808 | 825 | 97.9 % | 95.0 % | 0.021 |
| asked_mrt | 825 | 825 | 100.0 % | 89.0 % | 0.000 |
| asked_tlag | 825 | 825 | 100.0 % | 97.6 % | 0.000 |
| asked_tmax | 825 | 825 | 100.0 % | 91.2 % | 0.000 |
| asked_vz | 787 | 825 | 95.4 % | 91.0 % | 0.046 |
| auc_method | 755 | 825 | 91.5 % | 80.0 % | 0.076 |
| compare_pair | 813 | 825 | 98.5 % | 86.7 % | 0.011 |
| dose_has_unit | 825 | 825 | 100.0 % | 79.2 % | 0.000 |
| is_not_available | 790 | 825 | 95.8 % | 93.3 % | 0.041 |
| route | 821 | 825 | 99.5 % | 49.2 % | 0.005 |
| **overall** | 16207 | 16500 | **98.2 %** | 85.6 % | 0.016 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | not_supported | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|---|
| compare | 110 |  |  |  |  |  |  | 110 | 100.0 % |
| fit_pk1 |  | 55 |  |  |  |  |  | 55 | 100.0 % |
| fit_pk2 |  |  | 36 | 1 | 18 |  |  | 55 | 65.5 % |
| nca |  |  |  | 100 | 10 |  |  | 110 | 90.9 % |
| none_needed |  |  |  | 1 | 380 | 4 |  | 385 | 98.7 % |
| not_supported |  |  |  |  | 6 | 49 |  | 55 | 89.1 % |
| simulate |  |  |  |  |  |  | 55 | 55 | 100.0 % |

### Confusion: route (rows = gold, columns = predicted)

| gold \ pred | iv_bolus | iv_infusion | oral | unknown | total | recall |
|---|---|---|---|---|---|---|
| iv_bolus | 214 |  |  |  | 214 | 100.0 % |
| iv_infusion |  | 72 |  | 4 | 76 | 94.7 % |
| oral |  |  | 406 |  | 406 | 100.0 % |
| unknown |  |  |  | 129 | 129 | 100.0 % |

### Confusion: auc_method (rows = gold, columns = predicted)

| gold \ pred | lin_up_log_down | linear | not_applicable | total | recall |
|---|---|---|---|---|---|
| lin_up_log_down | 50 |  | 5 | 55 | 90.9 % |
| linear | 2 | 75 | 33 | 110 | 68.2 % |
| not_applicable | 22 | 8 | 630 | 660 | 95.5 % |

### Confusion: compare_pair (rows = gold, columns = predicted)

| gold \ pred | 2+3 | 3+2 | not_applicable | total | recall |
|---|---|---|---|---|---|
| 2+3 | 79 |  |  | 79 | 100.0 % |
| 3+2 | 12 | 19 |  | 31 | 61.3 % |
| not_applicable |  |  | 715 | 715 | 100.0 % |

### Confusion: is_not_available (rows = gold, columns = predicted)

| gold \ pred | false | true | total | recall |
|---|---|---|---|---|
| false | 770 |  | 770 | 100.0 % |
| true | 35 | 20 | 55 | 36.4 % |

### Calibration (all questions; probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 0 | - | - |
| [0.3, 0.4) | 1 | 0.339 | 0.000 |
| [0.4, 0.5) | 5 | 0.455 | 0.800 |
| [0.5, 0.6) | 16 | 0.540 | 0.438 |
| [0.6, 0.7) | 20 | 0.662 | 0.300 |
| [0.7, 0.8) | 24 | 0.744 | 0.417 |
| [0.8, 0.9) | 39 | 0.843 | 0.590 |
| [0.9, 1.0] | 16395 | 1.000 | 0.985 |

Expected calibration error: 0.016.

### Questions at or below the always-majority baseline

None: every question is above its baseline.

