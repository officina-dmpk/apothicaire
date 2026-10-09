# qwen35-0.8b-d01-merged on heldout (Unsloth decision model)

`decision/predict_unsloth.py`, `FastDecisionModel.predict`, one call per row. Gold is one-hot, so calibration is measured against a certain label; `noul` probabilities are P(true). Python 3.12.10, torch 2.14.1+cu130.

| run | rows | overall accuracy | ECE | ms per row | device/dtype |
|---|---|---|---|---|---|
| qwen35-0.8b-d01-merged, heldout | 720 | 99.9 % | 0.001 | 175.3 | cuda/bfloat16 |

## qwen35-0.8b-d01-merged, heldout

Rows 720, questions 14400, device cuda, dtype bfloat16, model load 23.6 s, inference wall 126.4 s (after 2 untimed warm-up rows).
Time per row (one call, 20 questions): mean 175.3 ms, median 176.7 ms, p95 178.6 ms. VRAM: nvidia-smi used 699 MiB before load, 2867 after the run; torch peak allocated 1935 MiB.

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 720 | 720 | 100.0 % | 58.3 % | 0.005 |
| asked_adj_r2 | 720 | 720 | 100.0 % | 93.9 % | 0.000 |
| asked_aucinf | 720 | 720 | 100.0 % | 88.5 % | 0.000 |
| asked_auclast | 720 | 720 | 100.0 % | 81.5 % | 0.000 |
| asked_aucpext | 720 | 720 | 100.0 % | 93.9 % | 0.000 |
| asked_c0 | 720 | 720 | 100.0 % | 93.6 % | 0.000 |
| asked_cl | 720 | 720 | 100.0 % | 84.4 % | 0.000 |
| asked_cmax | 720 | 720 | 100.0 % | 84.0 % | 0.000 |
| asked_half_life | 720 | 720 | 100.0 % | 84.6 % | 0.000 |
| asked_lambda_z | 720 | 720 | 100.0 % | 90.0 % | 0.000 |
| asked_lambda_z_points | 720 | 720 | 100.0 % | 92.9 % | 0.000 |
| asked_mrt | 720 | 720 | 100.0 % | 88.3 % | 0.000 |
| asked_tlag | 720 | 720 | 100.0 % | 96.1 % | 0.000 |
| asked_tmax | 720 | 720 | 100.0 % | 84.4 % | 0.000 |
| asked_vz | 720 | 720 | 100.0 % | 85.1 % | 0.000 |
| auc_method | 720 | 720 | 100.0 % | 83.3 % | 0.001 |
| compare_pair | 720 | 720 | 100.0 % | 91.7 % | 0.000 |
| dose_has_unit | 720 | 720 | 100.0 % | 81.8 % | 0.000 |
| is_not_available | 706 | 720 | 98.1 % | 91.7 % | 0.014 |
| route | 720 | 720 | 100.0 % | 43.6 % | 0.000 |
| **overall** | 14386 | 14400 | **99.9 %** | 84.6 % | 0.001 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|
| compare | 60 |  |  |  |  |  | 60 | 100.0 % |
| fit_pk1 |  | 60 |  |  |  |  | 60 | 100.0 % |
| fit_pk2 |  |  | 60 |  |  |  | 60 | 100.0 % |
| nca |  |  |  | 60 |  |  | 60 | 100.0 % |
| none_needed |  |  |  |  | 420 |  | 420 | 100.0 % |
| simulate |  |  |  |  |  | 60 | 60 | 100.0 % |

### Confusion: route (rows = gold, columns = predicted)

| gold \ pred | iv_bolus | iv_infusion | oral | unknown | total | recall |
|---|---|---|---|---|---|---|
| iv_bolus | 231 |  |  |  | 231 | 100.0 % |
| iv_infusion |  | 89 |  |  | 89 | 100.0 % |
| oral |  |  | 314 |  | 314 | 100.0 % |
| unknown |  |  |  | 86 | 86 | 100.0 % |

### Confusion: auc_method (rows = gold, columns = predicted)

| gold \ pred | lin_up_log_down | linear | not_applicable | total | recall |
|---|---|---|---|---|---|
| lin_up_log_down | 60 |  |  | 60 | 100.0 % |
| linear |  | 60 |  | 60 | 100.0 % |
| not_applicable |  |  | 600 | 600 | 100.0 % |

### Confusion: compare_pair (rows = gold, columns = predicted)

| gold \ pred | 2+3 | not_applicable | total | recall |
|---|---|---|---|---|
| 2+3 | 60 |  | 60 | 100.0 % |
| not_applicable |  | 660 | 660 | 100.0 % |

### Confusion: is_not_available (rows = gold, columns = predicted)

| gold \ pred | false | true | total | recall |
|---|---|---|---|---|
| false | 659 | 1 | 660 | 99.8 % |
| true | 13 | 47 | 60 | 78.3 % |

### Calibration (all questions; probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 0 | - | - |
| [0.3, 0.4) | 0 | - | - |
| [0.4, 0.5) | 0 | - | - |
| [0.5, 0.6) | 14 | 0.554 | 0.643 |
| [0.6, 0.7) | 15 | 0.649 | 0.533 |
| [0.7, 0.8) | 17 | 0.763 | 1.000 |
| [0.8, 0.9) | 28 | 0.850 | 0.929 |
| [0.9, 1.0] | 14326 | 1.000 | 1.000 |

Expected calibration error: 0.001.

### Questions at or below the always-majority baseline

None: every question is above its baseline.

