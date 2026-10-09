# smoke-merged on heldout (Unsloth decision model)

`decision/predict_unsloth.py`, `FastDecisionModel.predict`, one call per row. Gold is one-hot, so calibration is measured against a certain label; `noul` probabilities are P(true). Python 3.12.10, torch 2.14.1+cu130.

| run | rows | overall accuracy | ECE | ms per row | device/dtype |
|---|---|---|---|---|---|
| smoke-merged, heldout, 8 rows (every 70th) | 8 | 71.2 % | 0.082 | 12410.1 | cpu/float32 |

## smoke-merged, heldout, 8 rows (every 70th)

Rows 8, questions 160, device cpu, dtype float32, model load 21.1 s, inference wall 99.3 s (after 1 untimed warm-up rows).
Time per row (one call, seven questions): mean 12410.1 ms, median 12349.5 ms, p95 13517.8 ms. VRAM: none (cpu).

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 3 | 8 | 37.5 % | 37.5 % | 0.134 |
| asked_adj_r2 | 8 | 8 | 100.0 % | 100.0 % | 0.286 |
| asked_aucinf | 6 | 8 | 75.0 % | 75.0 % | 0.055 |
| asked_auclast | 5 | 8 | 62.5 % | 62.5 % | 0.184 |
| asked_aucpext | 7 | 8 | 87.5 % | 87.5 % | 0.070 |
| asked_c0 | 8 | 8 | 100.0 % | 100.0 % | 0.192 |
| asked_cl | 5 | 8 | 62.5 % | 62.5 % | 0.182 |
| asked_cmax | 5 | 8 | 62.5 % | 62.5 % | 0.178 |
| asked_half_life | 5 | 8 | 62.5 % | 62.5 % | 0.182 |
| asked_lambda_z | 6 | 8 | 75.0 % | 75.0 % | 0.068 |
| asked_lambda_z_points | 8 | 8 | 100.0 % | 100.0 % | 0.192 |
| asked_mrt | 6 | 8 | 75.0 % | 75.0 % | 0.074 |
| asked_tlag | 8 | 8 | 100.0 % | 100.0 % | 0.180 |
| asked_tmax | 5 | 8 | 62.5 % | 62.5 % | 0.186 |
| asked_vz | 5 | 8 | 62.5 % | 62.5 % | 0.187 |
| auc_method | 5 | 8 | 62.5 % | 62.5 % | 0.039 |
| compare_pair | 7 | 8 | 87.5 % | 87.5 % | 0.283 |
| dose_has_unit | 0 | 8 | 0.0 % | 100.0 % | 0.729 |
| is_not_available | 8 | 8 | 100.0 % | 100.0 % | 0.209 |
| route | 4 | 8 | 50.0 % | 50.0 % | 0.295 |
| **overall** | 114 | 160 | **71.2 %** | 76.2 % | 0.082 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | total | recall |
|---|---|---|---|---|---|---|---|
| compare |  |  |  |  | 1 | 1 | 0.0 % |
| fit_pk1 |  |  |  |  | 1 | 1 | 0.0 % |
| fit_pk2 |  |  |  |  | 1 | 1 | 0.0 % |
| nca |  |  |  |  | 2 | 2 | 0.0 % |
| none_needed |  |  |  |  | 3 | 3 | 100.0 % |

### Calibration (all questions; probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 8 | 0.241 | 0.375 |
| [0.3, 0.4) | 2 | 0.397 | 0.000 |
| [0.4, 0.5) | 6 | 0.406 | 0.667 |
| [0.5, 0.6) | 12 | 0.562 | 0.750 |
| [0.6, 0.7) | 4 | 0.670 | 0.750 |
| [0.7, 0.8) | 28 | 0.753 | 0.571 |
| [0.8, 0.9) | 100 | 0.811 | 0.790 |
| [0.9, 1.0] | 0 | - | - |

Expected calibration error: 0.082.
