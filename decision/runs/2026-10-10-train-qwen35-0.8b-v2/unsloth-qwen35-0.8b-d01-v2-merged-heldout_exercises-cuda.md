# qwen35-0.8b-d01-v2-merged on heldout_exercises (Unsloth decision model)

`decision/predict_unsloth.py`, `FastDecisionModel.predict`, one call per row. Gold is one-hot, so calibration is measured against a certain label; `noul` probabilities are P(true). Python 3.12.10, torch 2.14.1+cu130.

| run | rows | overall accuracy | ECE | ms per row | device/dtype |
|---|---|---|---|---|---|
| qwen35-0.8b-d01-v2-merged, heldout_exercises | 920 | 99.5 % | 0.004 | 178.7 | cuda/bfloat16 |

## qwen35-0.8b-d01-v2-merged, heldout_exercises

Rows 920, questions 18400, device cuda, dtype bfloat16, model load 23.2 s, inference wall 164.5 s (after 2 untimed warm-up rows).
Time per row (one call, 20 questions): mean 178.7 ms, median 178.6 ms, p95 181.1 ms. VRAM: nvidia-smi used 686 MiB before load, 2947 after the run; torch peak allocated 2086 MiB.

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 912 | 920 | 99.1 % | 45.7 % | 0.007 |
| asked_adj_r2 | 920 | 920 | 100.0 % | 93.8 % | 0.000 |
| asked_aucinf | 920 | 920 | 100.0 % | 91.3 % | 0.000 |
| asked_auclast | 920 | 920 | 100.0 % | 82.2 % | 0.000 |
| asked_aucpext | 920 | 920 | 100.0 % | 94.1 % | 0.000 |
| asked_c0 | 920 | 920 | 100.0 % | 95.2 % | 0.000 |
| asked_cl | 920 | 920 | 100.0 % | 90.3 % | 0.001 |
| asked_cmax | 920 | 920 | 100.0 % | 86.8 % | 0.000 |
| asked_half_life | 920 | 920 | 100.0 % | 87.5 % | 0.000 |
| asked_lambda_z | 920 | 920 | 100.0 % | 92.1 % | 0.000 |
| asked_lambda_z_points | 920 | 920 | 100.0 % | 95.4 % | 0.000 |
| asked_mrt | 920 | 920 | 100.0 % | 92.4 % | 0.000 |
| asked_tlag | 920 | 920 | 100.0 % | 96.3 % | 0.000 |
| asked_tmax | 920 | 920 | 100.0 % | 87.6 % | 0.000 |
| asked_vz | 920 | 920 | 100.0 % | 89.0 % | 0.000 |
| auc_method | 905 | 920 | 98.4 % | 78.3 % | 0.008 |
| compare_pair | 913 | 920 | 99.2 % | 87.0 % | 0.002 |
| dose_has_unit | 916 | 920 | 99.6 % | 81.4 % | 0.004 |
| is_not_available | 860 | 920 | 93.5 % | 93.5 % | 0.065 |
| route | 920 | 920 | 100.0 % | 44.3 % | 0.000 |
| **overall** | 18306 | 18400 | **99.5 %** | 85.2 % | 0.004 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | not_supported | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|---|
| compare | 120 |  |  |  |  |  |  | 120 | 100.0 % |
| fit_pk1 |  | 55 |  |  | 5 |  |  | 60 | 91.7 % |
| fit_pk2 |  |  | 60 |  |  |  |  | 60 | 100.0 % |
| nca |  |  |  | 140 |  |  |  | 140 | 100.0 % |
| none_needed |  |  |  |  | 420 |  |  | 420 | 100.0 % |
| not_supported |  |  |  | 2 | 1 | 57 |  | 60 | 95.0 % |
| simulate |  |  |  |  |  |  | 60 | 60 | 100.0 % |

### Confusion: route (rows = gold, columns = predicted)

| gold \ pred | iv_bolus | iv_infusion | oral | unknown | total | recall |
|---|---|---|---|---|---|---|
| iv_bolus | 285 |  |  |  | 285 | 100.0 % |
| iv_infusion |  | 118 |  |  | 118 | 100.0 % |
| oral |  |  | 408 |  | 408 | 100.0 % |
| unknown |  |  |  | 109 | 109 | 100.0 % |

### Confusion: auc_method (rows = gold, columns = predicted)

| gold \ pred | lin_up_log_down | linear | not_applicable | total | recall |
|---|---|---|---|---|---|
| lin_up_log_down | 75 |  |  | 75 | 100.0 % |
| linear |  | 114 | 11 | 125 | 91.2 % |
| not_applicable | 4 |  | 716 | 720 | 99.4 % |

### Confusion: compare_pair (rows = gold, columns = predicted)

| gold \ pred | 2+3 | 3+2 | not_applicable | total | recall |
|---|---|---|---|---|---|
| 2+3 | 89 |  |  | 89 | 100.0 % |
| 3+2 | 7 | 24 |  | 31 | 77.4 % |
| not_applicable |  |  | 800 | 800 | 100.0 % |

### Confusion: is_not_available (rows = gold, columns = predicted)

| gold \ pred | false | true | total | recall |
|---|---|---|---|---|
| false | 860 |  | 860 | 100.0 % |
| true | 60 |  | 60 | 0.0 % |

### Calibration (all questions; probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 0 | - | - |
| [0.3, 0.4) | 0 | - | - |
| [0.4, 0.5) | 0 | - | - |
| [0.5, 0.6) | 10 | 0.563 | 0.600 |
| [0.6, 0.7) | 11 | 0.657 | 0.636 |
| [0.7, 0.8) | 17 | 0.759 | 0.765 |
| [0.8, 0.9) | 35 | 0.856 | 0.800 |
| [0.9, 1.0] | 18327 | 1.000 | 0.996 |

Expected calibration error: 0.004.

### Questions at or below the always-majority baseline

| question | accuracy | always-majority | difference (points) |
|---|---|---|---|
| is_not_available | 93.5 % | 93.5 % | +0.0 |

