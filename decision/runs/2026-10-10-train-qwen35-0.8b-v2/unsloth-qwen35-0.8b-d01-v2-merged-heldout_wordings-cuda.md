# qwen35-0.8b-d01-v2-merged on heldout_wordings (Unsloth decision model)

`decision/predict_unsloth.py`, `FastDecisionModel.predict`, one call per row. Gold is one-hot, so calibration is measured against a certain label; `noul` probabilities are P(true). Python 3.12.10, torch 2.14.1+cu130.

| run | rows | overall accuracy | ECE | ms per row | device/dtype |
|---|---|---|---|---|---|
| qwen35-0.8b-d01-v2-merged, heldout_wordings | 825 | 97.9 % | 0.019 | 177.7 | cuda/bfloat16 |

## qwen35-0.8b-d01-v2-merged, heldout_wordings

Rows 825, questions 16500, device cuda, dtype bfloat16, model load 22.6 s, inference wall 146.7 s (after 2 untimed warm-up rows).
Time per row (one call, 20 questions): mean 177.7 ms, median 177.7 ms, p95 180.3 ms. VRAM: nvidia-smi used 686 MiB before load, 2807 after the run; torch peak allocated 1947 MiB.

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 780 | 825 | 94.5 % | 46.7 % | 0.045 |
| asked_adj_r2 | 825 | 825 | 100.0 % | 93.9 % | 0.000 |
| asked_aucinf | 825 | 825 | 100.0 % | 88.5 % | 0.003 |
| asked_auclast | 795 | 825 | 96.4 % | 84.6 % | 0.036 |
| asked_aucpext | 824 | 825 | 99.9 % | 96.2 % | 0.001 |
| asked_c0 | 825 | 825 | 100.0 % | 95.6 % | 0.000 |
| asked_cl | 813 | 825 | 98.5 % | 92.8 % | 0.014 |
| asked_cmax | 796 | 825 | 96.5 % | 84.4 % | 0.034 |
| asked_half_life | 825 | 825 | 100.0 % | 82.7 % | 0.000 |
| asked_lambda_z | 812 | 825 | 98.4 % | 95.2 % | 0.016 |
| asked_lambda_z_points | 808 | 825 | 97.9 % | 95.0 % | 0.021 |
| asked_mrt | 819 | 825 | 99.3 % | 89.0 % | 0.006 |
| asked_tlag | 825 | 825 | 100.0 % | 97.6 % | 0.000 |
| asked_tmax | 825 | 825 | 100.0 % | 91.2 % | 0.000 |
| asked_vz | 787 | 825 | 95.4 % | 91.0 % | 0.046 |
| auc_method | 746 | 825 | 90.4 % | 80.0 % | 0.088 |
| compare_pair | 803 | 825 | 97.3 % | 86.7 % | 0.022 |
| dose_has_unit | 825 | 825 | 100.0 % | 79.2 % | 0.000 |
| is_not_available | 770 | 825 | 93.3 % | 93.3 % | 0.067 |
| route | 821 | 825 | 99.5 % | 49.2 % | 0.005 |
| **overall** | 16149 | 16500 | **97.9 %** | 85.6 % | 0.019 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | not_supported | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|---|
| compare | 110 |  |  |  |  |  |  | 110 | 100.0 % |
| fit_pk1 |  | 55 |  |  |  |  |  | 55 | 100.0 % |
| fit_pk2 |  |  | 39 | 1 | 15 |  |  | 55 | 70.9 % |
| nca |  |  |  | 97 | 13 |  |  | 110 | 88.2 % |
| none_needed |  |  |  | 4 | 381 |  |  | 385 | 99.0 % |
| not_supported |  |  |  |  | 12 | 43 |  | 55 | 78.2 % |
| simulate |  |  |  |  |  |  | 55 | 55 | 100.0 % |

### Confusion: route (rows = gold, columns = predicted)

| gold \ pred | iv_bolus | iv_infusion | oral | unknown | total | recall |
|---|---|---|---|---|---|---|
| iv_bolus | 213 | 1 |  |  | 214 | 99.5 % |
| iv_infusion | 1 | 73 |  | 2 | 76 | 96.1 % |
| oral |  |  | 406 |  | 406 | 100.0 % |
| unknown |  |  |  | 129 | 129 | 100.0 % |

### Confusion: auc_method (rows = gold, columns = predicted)

| gold \ pred | lin_up_log_down | linear | not_applicable | total | recall |
|---|---|---|---|---|---|
| lin_up_log_down | 54 |  | 1 | 55 | 98.2 % |
| linear |  | 54 | 56 | 110 | 49.1 % |
| not_applicable | 22 |  | 638 | 660 | 96.7 % |

### Confusion: compare_pair (rows = gold, columns = predicted)

| gold \ pred | 2+3 | 3+2 | not_applicable | total | recall |
|---|---|---|---|---|---|
| 2+3 | 79 |  |  | 79 | 100.0 % |
| 3+2 | 22 | 9 |  | 31 | 29.0 % |
| not_applicable |  |  | 715 | 715 | 100.0 % |

### Confusion: is_not_available (rows = gold, columns = predicted)

| gold \ pred | false | true | total | recall |
|---|---|---|---|---|
| false | 770 |  | 770 | 100.0 % |
| true | 55 |  | 55 | 0.0 % |

### Calibration (all questions; probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 0 | - | - |
| [0.3, 0.4) | 0 | - | - |
| [0.4, 0.5) | 0 | - | - |
| [0.5, 0.6) | 22 | 0.547 | 0.636 |
| [0.6, 0.7) | 18 | 0.659 | 0.278 |
| [0.7, 0.8) | 30 | 0.760 | 0.433 |
| [0.8, 0.9) | 44 | 0.856 | 0.705 |
| [0.9, 1.0] | 16386 | 1.000 | 0.982 |

Expected calibration error: 0.019.

### Questions at or below the always-majority baseline

| question | accuracy | always-majority | difference (points) |
|---|---|---|---|
| is_not_available | 93.3 % | 93.3 % | +0.0 |

