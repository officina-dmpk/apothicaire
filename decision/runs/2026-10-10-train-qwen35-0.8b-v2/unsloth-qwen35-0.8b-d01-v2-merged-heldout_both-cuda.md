# qwen35-0.8b-d01-v2-merged on heldout_both (Unsloth decision model)

`decision/predict_unsloth.py`, `FastDecisionModel.predict`, one call per row. Gold is one-hot, so calibration is measured against a certain label; `noul` probabilities are P(true). Python 3.12.10, torch 2.14.1+cu130.

| run | rows | overall accuracy | ECE | ms per row | device/dtype |
|---|---|---|---|---|---|
| qwen35-0.8b-d01-v2-merged, heldout_both | 593 | 97.8 % | 0.020 | 177.6 | cuda/bfloat16 |

## qwen35-0.8b-d01-v2-merged, heldout_both

Rows 593, questions 11860, device cuda, dtype bfloat16, model load 22.4 s, inference wall 105.4 s (after 2 untimed warm-up rows).
Time per row (one call, 20 questions): mean 177.6 ms, median 177.2 ms, p95 180.0 ms. VRAM: nvidia-smi used 686 MiB before load, 2807 after the run; torch peak allocated 1944 MiB.

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 565 | 593 | 95.3 % | 46.0 % | 0.045 |
| asked_adj_r2 | 593 | 593 | 100.0 % | 93.9 % | 0.000 |
| asked_aucinf | 593 | 593 | 100.0 % | 90.4 % | 0.001 |
| asked_auclast | 575 | 593 | 97.0 % | 86.7 % | 0.030 |
| asked_aucpext | 592 | 593 | 99.8 % | 96.3 % | 0.003 |
| asked_c0 | 593 | 593 | 100.0 % | 95.4 % | 0.000 |
| asked_cl | 578 | 593 | 97.5 % | 93.1 % | 0.024 |
| asked_cmax | 579 | 593 | 97.6 % | 85.7 % | 0.024 |
| asked_half_life | 593 | 593 | 100.0 % | 82.1 % | 0.000 |
| asked_lambda_z | 583 | 593 | 98.3 % | 94.3 % | 0.014 |
| asked_lambda_z_points | 578 | 593 | 97.5 % | 93.9 % | 0.025 |
| asked_mrt | 589 | 593 | 99.3 % | 89.7 % | 0.008 |
| asked_tlag | 593 | 593 | 100.0 % | 98.5 % | 0.000 |
| asked_tmax | 593 | 593 | 100.0 % | 92.1 % | 0.000 |
| asked_vz | 569 | 593 | 96.0 % | 92.4 % | 0.040 |
| auc_method | 522 | 593 | 88.0 % | 79.8 % | 0.110 |
| compare_pair | 575 | 593 | 97.0 % | 86.5 % | 0.030 |
| dose_has_unit | 593 | 593 | 100.0 % | 78.4 % | 0.000 |
| is_not_available | 560 | 593 | 94.4 % | 94.4 % | 0.056 |
| route | 583 | 593 | 98.3 % | 41.5 % | 0.013 |
| **overall** | 11599 | 11860 | **97.8 %** | 85.6 % | 0.020 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | not_supported | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|---|
| compare | 80 |  |  |  |  |  |  | 80 | 100.0 % |
| fit_pk1 |  | 40 |  |  |  |  |  | 40 | 100.0 % |
| fit_pk2 |  |  | 29 |  | 11 |  |  | 40 | 72.5 % |
| nca |  |  |  | 73 | 7 |  |  | 80 | 91.2 % |
| none_needed |  |  |  | 2 | 271 |  |  | 273 | 99.3 % |
| not_supported |  |  |  |  | 8 | 32 |  | 40 | 80.0 % |
| simulate |  |  |  |  |  |  | 40 | 40 | 100.0 % |

### Confusion: route (rows = gold, columns = predicted)

| gold \ pred | iv_bolus | iv_infusion | oral | unknown | total | recall |
|---|---|---|---|---|---|---|
| iv_bolus | 157 |  |  |  | 157 | 100.0 % |
| iv_infusion | 7 | 61 |  | 3 | 71 | 85.9 % |
| oral |  |  | 246 |  | 246 | 100.0 % |
| unknown |  |  |  | 119 | 119 | 100.0 % |

### Confusion: auc_method (rows = gold, columns = predicted)

| gold \ pred | lin_up_log_down | linear | not_applicable | total | recall |
|---|---|---|---|---|---|
| lin_up_log_down | 40 |  |  | 40 | 100.0 % |
| linear |  | 27 | 53 | 80 | 33.8 % |
| not_applicable | 18 |  | 455 | 473 | 96.2 % |

### Confusion: compare_pair (rows = gold, columns = predicted)

| gold \ pred | 2+3 | 3+2 | not_applicable | total | recall |
|---|---|---|---|---|---|
| 2+3 | 55 |  |  | 55 | 100.0 % |
| 3+2 | 18 | 7 |  | 25 | 28.0 % |
| not_applicable |  |  | 513 | 513 | 100.0 % |

### Confusion: is_not_available (rows = gold, columns = predicted)

| gold \ pred | false | true | total | recall |
|---|---|---|---|---|
| false | 560 |  | 560 | 100.0 % |
| true | 33 |  | 33 | 0.0 % |

### Calibration (all questions; probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 0 | - | - |
| [0.3, 0.4) | 0 | - | - |
| [0.4, 0.5) | 1 | 0.439 | 1.000 |
| [0.5, 0.6) | 21 | 0.554 | 0.571 |
| [0.6, 0.7) | 6 | 0.643 | 0.667 |
| [0.7, 0.8) | 28 | 0.758 | 0.250 |
| [0.8, 0.9) | 41 | 0.853 | 0.707 |
| [0.9, 1.0] | 11763 | 1.000 | 0.982 |

Expected calibration error: 0.020.

### Questions at or below the always-majority baseline

| question | accuracy | always-majority | difference (points) |
|---|---|---|---|
| is_not_available | 94.4 % | 94.4 % | +0.0 |

