# qwen35-0.8b-d01-v2-adapters on heldout_both (Unsloth decision model)

`decision/predict_unsloth.py`, `FastDecisionModel.predict`, one call per row. Gold is one-hot, so calibration is measured against a certain label; `noul` probabilities are P(true). Python 3.12.10, torch 2.14.1+cu130.

| run | rows | overall accuracy | ECE | ms per row | device/dtype |
|---|---|---|---|---|---|
| qwen35-0.8b-d01-v2-adapters, heldout_both | 593 | 98.2 % | 0.016 | 206.6 | cuda/bfloat16 |

## qwen35-0.8b-d01-v2-adapters, heldout_both

Rows 593, questions 11860, device cuda, dtype bfloat16, model load 23.6 s, inference wall 122.6 s (after 2 untimed warm-up rows).
Time per row (one call, 20 questions): mean 206.6 ms, median 206.3 ms, p95 209.3 ms. VRAM: nvidia-smi used 686 MiB before load, 2325 after the run; torch peak allocated 1443 MiB.

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 564 | 593 | 95.1 % | 46.0 % | 0.029 |
| asked_adj_r2 | 593 | 593 | 100.0 % | 93.9 % | 0.000 |
| asked_aucinf | 592 | 593 | 99.8 % | 90.4 % | 0.002 |
| asked_auclast | 575 | 593 | 97.0 % | 86.7 % | 0.027 |
| asked_aucpext | 593 | 593 | 100.0 % | 96.3 % | 0.000 |
| asked_c0 | 593 | 593 | 100.0 % | 95.4 % | 0.000 |
| asked_cl | 578 | 593 | 97.5 % | 93.1 % | 0.025 |
| asked_cmax | 579 | 593 | 97.6 % | 85.7 % | 0.024 |
| asked_half_life | 593 | 593 | 100.0 % | 82.1 % | 0.000 |
| asked_lambda_z | 586 | 593 | 98.8 % | 94.3 % | 0.012 |
| asked_lambda_z_points | 578 | 593 | 97.5 % | 93.9 % | 0.025 |
| asked_mrt | 593 | 593 | 100.0 % | 89.7 % | 0.000 |
| asked_tlag | 593 | 593 | 100.0 % | 98.5 % | 0.000 |
| asked_tmax | 593 | 593 | 100.0 % | 92.1 % | 0.000 |
| asked_vz | 569 | 593 | 96.0 % | 92.4 % | 0.040 |
| auc_method | 538 | 593 | 90.7 % | 79.8 % | 0.083 |
| compare_pair | 581 | 593 | 98.0 % | 86.5 % | 0.019 |
| dose_has_unit | 593 | 593 | 100.0 % | 78.4 % | 0.000 |
| is_not_available | 571 | 593 | 96.3 % | 94.4 % | 0.036 |
| route | 588 | 593 | 99.2 % | 41.5 % | 0.009 |
| **overall** | 11643 | 11860 | **98.2 %** | 85.6 % | 0.016 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | not_supported | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|---|
| compare | 80 |  |  |  |  |  |  | 80 | 100.0 % |
| fit_pk1 |  | 40 |  |  |  |  |  | 40 | 100.0 % |
| fit_pk2 |  |  | 22 | 2 | 14 | 2 |  | 40 | 55.0 % |
| nca |  |  |  | 75 | 5 |  |  | 80 | 93.8 % |
| none_needed |  |  |  | 1 | 272 |  |  | 273 | 99.6 % |
| not_supported |  |  |  |  | 5 | 35 |  | 40 | 87.5 % |
| simulate |  |  |  |  |  |  | 40 | 40 | 100.0 % |

### Confusion: route (rows = gold, columns = predicted)

| gold \ pred | iv_bolus | iv_infusion | oral | unknown | total | recall |
|---|---|---|---|---|---|---|
| iv_bolus | 157 |  |  |  | 157 | 100.0 % |
| iv_infusion |  | 66 |  | 5 | 71 | 93.0 % |
| oral |  |  | 246 |  | 246 | 100.0 % |
| unknown |  |  |  | 119 | 119 | 100.0 % |

### Confusion: auc_method (rows = gold, columns = predicted)

| gold \ pred | lin_up_log_down | linear | not_applicable | total | recall |
|---|---|---|---|---|---|
| lin_up_log_down | 37 |  | 3 | 40 | 92.5 % |
| linear | 3 | 51 | 26 | 80 | 63.8 % |
| not_applicable | 18 | 5 | 450 | 473 | 95.1 % |

### Confusion: compare_pair (rows = gold, columns = predicted)

| gold \ pred | 2+3 | 3+2 | not_applicable | total | recall |
|---|---|---|---|---|---|
| 2+3 | 55 |  |  | 55 | 100.0 % |
| 3+2 | 12 | 13 |  | 25 | 52.0 % |
| not_applicable |  |  | 513 | 513 | 100.0 % |

### Confusion: is_not_available (rows = gold, columns = predicted)

| gold \ pred | false | true | total | recall |
|---|---|---|---|---|
| false | 560 |  | 560 | 100.0 % |
| true | 22 | 11 | 33 | 33.3 % |

### Calibration (all questions; probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 0 | - | - |
| [0.3, 0.4) | 1 | 0.315 | 0.000 |
| [0.4, 0.5) | 2 | 0.470 | 0.500 |
| [0.5, 0.6) | 12 | 0.549 | 0.333 |
| [0.6, 0.7) | 22 | 0.641 | 0.455 |
| [0.7, 0.8) | 14 | 0.755 | 0.286 |
| [0.8, 0.9) | 23 | 0.854 | 0.522 |
| [0.9, 1.0] | 11786 | 1.000 | 0.985 |

Expected calibration error: 0.016.

### Questions at or below the always-majority baseline

None: every question is above its baseline.

