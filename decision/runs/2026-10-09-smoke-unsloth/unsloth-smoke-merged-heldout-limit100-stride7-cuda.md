# smoke-merged on heldout (Unsloth decision model)

`decision/predict_unsloth.py`, `FastDecisionModel.predict`, one call per row. Gold is one-hot, so calibration is measured against a certain label; `noul` probabilities are P(true). Python 3.12.10, torch 2.14.1+cu130.

| run | rows | overall accuracy | ECE | ms per row | device/dtype |
|---|---|---|---|---|---|
| smoke-merged, heldout, 100 rows (every 7th) | 100 | 79.7 % | 0.124 | 208.7 | cuda/bfloat16 |

## smoke-merged, heldout, 100 rows (every 7th)

Rows 100, questions 2000, device cuda, dtype bfloat16, model load 26.8 s, inference wall 20.9 s (after 2 untimed warm-up rows).
Time per row (one call, seven questions): mean 208.7 ms, median 203.9 ms, p95 237.7 ms. VRAM: nvidia-smi used 1284 MiB before load, 3707 after the run; torch peak allocated 2138 MiB.

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 61 | 100 | 61.0 % | 61.0 % | 0.367 |
| asked_adj_r2 | 97 | 100 | 97.0 % | 97.0 % | 0.258 |
| asked_aucinf | 89 | 100 | 89.0 % | 89.0 % | 0.085 |
| asked_auclast | 78 | 100 | 78.0 % | 78.0 % | 0.030 |
| asked_aucpext | 87 | 100 | 87.0 % | 87.0 % | 0.065 |
| asked_c0 | 97 | 100 | 97.0 % | 97.0 % | 0.162 |
| asked_cl | 86 | 100 | 86.0 % | 86.0 % | 0.130 |
| asked_cmax | 85 | 100 | 85.0 % | 85.0 % | 0.077 |
| asked_half_life | 81 | 100 | 81.0 % | 81.0 % | 0.080 |
| asked_lambda_z | 92 | 100 | 92.0 % | 92.0 % | 0.102 |
| asked_lambda_z_points | 96 | 100 | 96.0 % | 96.0 % | 0.151 |
| asked_mrt | 89 | 100 | 89.0 % | 89.0 % | 0.064 |
| asked_tlag | 94 | 100 | 94.0 % | 94.0 % | 0.119 |
| asked_tmax | 86 | 100 | 86.0 % | 86.0 % | 0.049 |
| asked_vz | 86 | 100 | 86.0 % | 86.0 % | 0.124 |
| auc_method | 80 | 100 | 80.0 % | 80.0 % | 0.213 |
| compare_pair | 88 | 100 | 88.0 % | 88.0 % | 0.269 |
| dose_has_unit | 17 | 100 | 17.0 % | 83.0 % | 0.560 |
| is_not_available | 91 | 100 | 91.0 % | 91.0 % | 0.117 |
| route | 13 | 100 | 13.0 % | 39.0 % | 0.275 |
| **overall** | 1593 | 2000 | **79.7 %** | 84.2 % | 0.124 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|
| compare |  |  |  |  | 12 |  | 12 | 0.0 % |
| fit_pk1 |  |  |  |  | 9 |  | 9 | 0.0 % |
| fit_pk2 |  |  |  |  | 6 |  | 6 | 0.0 % |
| nca |  |  |  |  | 8 |  | 8 | 0.0 % |
| none_needed |  |  |  |  | 61 |  | 61 | 100.0 % |
| simulate |  |  |  |  | 4 |  | 4 | 0.0 % |

### Calibration (all questions; probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 100 | 0.243 | 0.610 |
| [0.3, 0.4) | 32 | 0.397 | 0.031 |
| [0.4, 0.5) | 68 | 0.408 | 0.176 |
| [0.5, 0.6) | 136 | 0.567 | 0.853 |
| [0.6, 0.7) | 64 | 0.668 | 0.812 |
| [0.7, 0.8) | 321 | 0.749 | 0.651 |
| [0.8, 0.9) | 1279 | 0.812 | 0.893 |
| [0.9, 1.0] | 0 | - | - |

Expected calibration error: 0.124.
