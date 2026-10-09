# Zero-shot baseline of d1 on the typed-decisions rows (D-01, step 2)

No training. `decision/zero_shot_d1.py`, the model card's `system_one(state, questions)`, one call per row (seven questions: five `choice`, two `noul`).
Environment: python 3.12.10, torch 2.14.1+cu130, transformers 5.19.0, GPU: NVIDIA GeForce RTX 3060, none.
Gold is one-hot (the truth is known), so calibration is measured against a certain label. `noul` probabilities come from P(true).

## Summary

| run | rows | overall accuracy | ECE | ms per row | device/dtype |
|---|---|---|---|---|---|
| d1-3B, heldout, 120 rows (every 6th) | 120 | 66.3 % | 0.101 | 14159.5 | cpu/float32 |
| d1-omni-600M, heldout, 120 rows (every 6th) | 120 | 63.1 % | 0.083 | 136.3 | cuda/float16 |
| d1-omni-600M, heldout | 720 | 61.8 % | 0.084 | 133.8 | cuda/float16 |
| d1-3B, bench, 112 rows (every 8th) | 112 | 66.8 % | 0.090 | 14181.9 | cpu/float32 |
| d1-omni-600M, bench, 112 rows (every 8th) | 112 | 65.2 % | 0.087 | 136.4 | cuda/float16 |
| d1-omni-600M, bench | 900 | 62.2 % | 0.076 | 139.6 | cuda/float16 |
| d1-3B, heldout, first 10 rows | 10 | 65.7 % | 0.104 | 14144.0 | cpu/float32 |
| d1-omni-600M, heldout, first 20 rows | 20 | 66.4 % | 0.111 | 131.9 | cuda/float16 |

## d1-3B, heldout, 120 rows (every 6th)

Rows 120, questions 840, device cpu, dtype float32, model load 11.7 s, inference wall 1699.2 s (after 1 untimed warm-up rows).
Time per row (one call, seven questions): mean 14159.5 ms, median 14120.7 ms, p95 14583.4 ms. VRAM: none (cpu).

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 108 | 120 | 90.0 % | 55.0 % | 0.217 |
| auc_method | 91 | 120 | 75.8 % | 86.7 % | 0.109 |
| compare_pair | 26 | 120 | 21.7 % | 93.3 % | 0.475 |
| dose_has_unit | 105 | 120 | 87.5 % | 73.3 % | 0.065 |
| is_not_available | 34 | 120 | 28.3 % | 89.2 % | 0.398 |
| parameter_asked | 104 | 120 | 86.7 % | 44.2 % | 0.104 |
| route | 89 | 120 | 74.2 % | 45.0 % | 0.049 |
| **overall** | 557 | 840 | **66.3 %** | 69.5 % | 0.101 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|
| compare | 8 |  |  |  |  |  | 8 | 100.0 % |
| fit_pk1 |  | 8 |  |  |  |  | 8 | 100.0 % |
| fit_pk2 |  |  | 19 |  |  |  | 19 | 100.0 % |
| nca |  |  |  | 8 |  |  | 8 | 100.0 % |
| none_needed | 2 | 2 | 5 | 1 | 54 | 2 | 66 | 81.8 % |
| simulate |  |  |  |  |  | 11 | 11 | 100.0 % |

### Confusion: parameter_asked (rows = gold, columns = predicted)

| gold \ pred | adj_r2 | aucinf | auclast | aucpext | c0 | cl | cmax | half_life | lambda_z | lambda_z_points | mrt | none | several | tlag | vz | total | recall |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| adj_r2 |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 | 0.0 % |
| aucinf |  | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  | 1 | 100.0 % |
| auclast |  |  | 11 |  |  |  |  |  |  |  |  | 1 |  |  |  | 12 | 91.7 % |
| aucpext |  |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  | 1 | 100.0 % |
| c0 |  |  |  |  | 8 |  |  |  |  |  |  |  |  |  |  | 8 | 100.0 % |
| cl |  |  |  |  |  | 2 |  |  |  |  |  |  |  |  |  | 2 | 100.0 % |
| cmax |  |  |  |  |  |  | 2 |  |  |  |  |  |  |  |  | 2 | 100.0 % |
| half_life |  |  |  |  |  |  |  | 1 |  |  |  |  |  |  |  | 1 | 100.0 % |
| lambda_z |  |  |  |  |  |  |  |  | 3 |  |  |  |  |  |  | 3 | 100.0 % |
| lambda_z_points |  |  |  |  |  |  |  |  |  | 4 |  |  |  |  |  | 4 | 100.0 % |
| mrt |  |  |  |  |  |  |  |  |  |  |  |  | 3 |  |  | 3 | 0.0 % |
| none |  |  |  |  |  |  |  |  |  |  |  | 13 | 9 |  |  | 22 | 59.1 % |
| several |  |  |  |  |  |  | 2 |  |  |  |  |  | 51 |  |  | 53 | 96.2 % |
| tlag |  |  |  |  |  |  |  |  |  |  |  |  |  | 6 |  | 6 | 100.0 % |
| vz |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 1 | 1 | 100.0 % |

### Calibration (all questions; probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 3 | 0.292 | 0.000 |
| [0.3, 0.4) | 11 | 0.359 | 0.455 |
| [0.4, 0.5) | 46 | 0.456 | 0.674 |
| [0.5, 0.6) | 167 | 0.549 | 0.407 |
| [0.6, 0.7) | 143 | 0.648 | 0.573 |
| [0.7, 0.8) | 115 | 0.753 | 0.661 |
| [0.8, 0.9) | 124 | 0.849 | 0.710 |
| [0.9, 1.0] | 231 | 0.944 | 0.896 |

Expected calibration error: 0.101.

## d1-omni-600M, heldout, 120 rows (every 6th)

Rows 120, questions 840, device cuda, dtype float16, model load 6.1 s, inference wall 16.4 s (after 2 untimed warm-up rows).
Time per row (one call, seven questions): mean 136.3 ms, median 137.0 ms, p95 143.5 ms. VRAM: nvidia-smi used 658 MiB before load, 1887 after load, 2501 after the run (of 12288); torch peak allocated 1291 MiB.

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 82 | 120 | 68.3 % | 55.0 % | 0.211 |
| auc_method | 73 | 120 | 60.8 % | 86.7 % | 0.118 |
| compare_pair | 55 | 120 | 45.8 % | 93.3 % | 0.176 |
| dose_has_unit | 91 | 120 | 75.8 % | 73.3 % | 0.141 |
| is_not_available | 85 | 120 | 70.8 % | 89.2 % | 0.071 |
| parameter_asked | 62 | 120 | 51.7 % | 44.2 % | 0.212 |
| route | 82 | 120 | 68.3 % | 45.0 % | 0.086 |
| **overall** | 530 | 840 | **63.1 %** | 69.5 % | 0.083 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|
| compare | 5 |  |  | 1 | 2 |  | 8 | 62.5 % |
| fit_pk1 |  | 7 |  |  | 1 |  | 8 | 87.5 % |
| fit_pk2 |  | 3 | 16 |  |  |  | 19 | 84.2 % |
| nca |  | 2 |  | 6 |  |  | 8 | 75.0 % |
| none_needed |  | 1 | 1 | 9 | 39 | 16 | 66 | 59.1 % |
| simulate |  | 2 |  |  |  | 9 | 11 | 81.8 % |

### Confusion: parameter_asked (rows = gold, columns = predicted)

| gold \ pred | adj_r2 | aucinf | auclast | aucpext | c0 | cl | cmax | half_life | lambda_z | lambda_z_points | mrt | none | several | tlag | tmax | vz | total | recall |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| adj_r2 |  |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 | 0.0 % |
| aucinf |  | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 1 | 100.0 % |
| auclast |  |  | 5 |  |  |  |  |  |  |  |  | 5 | 2 |  |  |  | 12 | 41.7 % |
| aucpext |  |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  |  | 1 | 100.0 % |
| c0 |  |  | 1 |  | 5 |  |  |  |  |  |  | 1 |  |  | 1 |  | 8 | 62.5 % |
| cl |  |  |  |  |  |  |  |  |  |  |  | 2 |  |  |  |  | 2 | 0.0 % |
| cmax |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 2 |  | 2 | 0.0 % |
| half_life |  |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 | 0.0 % |
| lambda_z |  |  |  |  |  |  |  |  | 3 |  |  |  |  |  |  |  | 3 | 100.0 % |
| lambda_z_points |  |  |  |  |  |  |  |  | 2 | 1 |  |  | 1 |  |  |  | 4 | 25.0 % |
| mrt |  |  |  |  |  |  |  |  |  |  | 2 | 1 |  |  |  |  | 3 | 66.7 % |
| none |  |  |  |  |  |  |  |  |  |  |  | 6 | 16 |  |  |  | 22 | 27.3 % |
| several |  |  |  | 1 |  | 1 | 2 |  | 3 | 1 |  | 10 | 31 |  | 4 |  | 53 | 58.5 % |
| tlag |  |  |  |  |  |  |  |  |  |  |  |  |  | 6 |  |  | 6 | 100.0 % |
| vz |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 1 | 1 | 100.0 % |

### Calibration (all questions; probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 34 | 0.166 | 0.382 |
| [0.2, 0.3) | 59 | 0.251 | 0.508 |
| [0.3, 0.4) | 86 | 0.351 | 0.488 |
| [0.4, 0.5) | 100 | 0.448 | 0.620 |
| [0.5, 0.6) | 182 | 0.552 | 0.527 |
| [0.6, 0.7) | 129 | 0.645 | 0.636 |
| [0.7, 0.8) | 75 | 0.743 | 0.747 |
| [0.8, 0.9) | 60 | 0.845 | 0.817 |
| [0.9, 1.0] | 115 | 0.958 | 0.870 |

Expected calibration error: 0.083.

## d1-omni-600M, heldout

Rows 720, questions 5040, device cuda, dtype float16, model load 5.9 s, inference wall 96.4 s (after 2 untimed warm-up rows).
Time per row (one call, seven questions): mean 133.8 ms, median 133.8 ms, p95 141.2 ms. VRAM: nvidia-smi used 644 MiB before load, 1871 after load, 2644 after the run (of 12288); torch peak allocated 1302 MiB.

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 482 | 720 | 66.9 % | 58.3 % | 0.237 |
| auc_method | 430 | 720 | 59.7 % | 83.3 % | 0.075 |
| compare_pair | 330 | 720 | 45.8 % | 91.7 % | 0.172 |
| dose_has_unit | 600 | 720 | 83.3 % | 81.8 % | 0.057 |
| is_not_available | 410 | 720 | 56.9 % | 91.7 % | 0.067 |
| parameter_asked | 342 | 720 | 47.5 % | 48.5 % | 0.192 |
| route | 521 | 720 | 72.4 % | 43.6 % | 0.076 |
| **overall** | 3115 | 5040 | **61.8 %** | 71.3 % | 0.084 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|
| compare | 23 |  | 1 | 3 | 28 | 5 | 60 | 38.3 % |
| fit_pk1 |  | 44 | 1 |  | 8 | 7 | 60 | 73.3 % |
| fit_pk2 |  | 12 | 46 | 2 |  |  | 60 | 76.7 % |
| nca |  | 12 | 1 | 46 | 1 |  | 60 | 76.7 % |
| none_needed |  | 14 | 2 | 63 | 283 | 58 | 420 | 67.4 % |
| simulate |  | 9 | 9 | 2 |  | 40 | 60 | 66.7 % |

### Confusion: parameter_asked (rows = gold, columns = predicted)

| gold \ pred | adj_r2 | aucinf | auclast | aucpext | c0 | cl | cmax | half_life | lambda_z | lambda_z_points | mrt | none | several | tlag | tmax | vz | total | recall |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| adj_r2 | 3 |  |  |  |  |  |  |  |  |  |  |  | 6 |  |  |  | 9 | 33.3 % |
| aucinf |  | 11 |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 11 | 100.0 % |
| auclast |  |  | 20 |  |  |  |  |  |  |  |  | 28 | 25 |  |  |  | 73 | 27.4 % |
| aucpext |  |  |  | 9 |  |  |  |  |  |  |  |  |  |  |  |  | 9 | 100.0 % |
| c0 |  |  | 1 | 2 | 20 |  |  |  |  |  |  | 3 | 4 |  | 3 |  | 33 | 60.6 % |
| cl |  |  |  |  |  |  |  |  |  |  |  | 13 |  |  |  |  | 13 | 0.0 % |
| cmax |  |  |  |  |  |  | 5 |  |  |  |  |  |  |  | 2 |  | 7 | 71.4 % |
| half_life |  |  |  |  |  |  |  |  |  |  |  |  | 16 |  |  |  | 16 | 0.0 % |
| lambda_z |  |  |  |  |  |  |  |  | 12 |  |  |  |  |  |  |  | 12 | 100.0 % |
| lambda_z_points |  |  |  |  |  |  |  |  | 8 | 4 |  |  | 3 |  | 1 |  | 16 | 25.0 % |
| mrt |  |  |  |  |  |  |  |  |  |  | 8 | 3 | 1 |  |  |  | 12 | 66.7 % |
| none |  |  |  |  |  |  |  |  |  |  |  | 46 | 74 |  |  |  | 120 | 38.3 % |
| several |  |  |  | 32 | 9 | 10 | 11 |  | 27 | 8 |  | 54 | 173 |  | 25 |  | 349 | 49.6 % |
| tlag |  |  |  |  |  |  |  |  |  |  |  | 2 | 6 | 20 |  |  | 28 | 71.4 % |
| tmax |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 4 |  | 4 | 100.0 % |
| vz |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  | 7 | 8 | 87.5 % |

### Calibration (all questions; probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 173 | 0.168 | 0.509 |
| [0.2, 0.3) | 411 | 0.251 | 0.462 |
| [0.3, 0.4) | 546 | 0.352 | 0.485 |
| [0.4, 0.5) | 607 | 0.449 | 0.585 |
| [0.5, 0.6) | 1094 | 0.549 | 0.516 |
| [0.6, 0.7) | 796 | 0.646 | 0.567 |
| [0.7, 0.8) | 440 | 0.744 | 0.739 |
| [0.8, 0.9) | 335 | 0.851 | 0.842 |
| [0.9, 1.0] | 638 | 0.959 | 0.931 |

Expected calibration error: 0.084.

## d1-3B, bench, 112 rows (every 8th)

Rows 112, questions 784, device cpu, dtype float32, model load 10.8 s, inference wall 1588.4 s (after 1 untimed warm-up rows).
Time per row (one call, seven questions): mean 14181.9 ms, median 14137.1 ms, p95 14792.1 ms. VRAM: none (cpu).

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 93 | 112 | 83.0 % | 59.8 % | 0.177 |
| auc_method | 76 | 112 | 67.9 % | 83.9 % | 0.123 |
| compare_pair | 27 | 112 | 24.1 % | 90.2 % | 0.478 |
| dose_has_unit | 103 | 112 | 92.0 % | 84.8 % | 0.047 |
| is_not_available | 33 | 112 | 29.5 % | 85.7 % | 0.402 |
| parameter_asked | 102 | 112 | 91.1 % | 42.0 % | 0.149 |
| route | 90 | 112 | 80.4 % | 45.5 % | 0.122 |
| **overall** | 524 | 784 | **66.8 %** | 70.3 % | 0.090 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|
| compare | 11 |  |  |  |  |  | 11 | 100.0 % |
| fit_pk1 |  | 7 |  |  |  |  | 7 | 100.0 % |
| fit_pk2 |  |  | 10 |  |  |  | 10 | 100.0 % |
| nca |  |  |  | 7 |  |  | 7 | 100.0 % |
| none_needed | 3 | 10 | 4 | 1 | 48 | 1 | 67 | 71.6 % |
| simulate |  |  |  |  |  | 10 | 10 | 100.0 % |

### Confusion: parameter_asked (rows = gold, columns = predicted)

| gold \ pred | adj_r2 | aucinf | auclast | c0 | half_life | lambda_z | lambda_z_points | mrt | none | several | tlag | tmax | vz | total | recall |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| adj_r2 |  |  |  |  |  |  |  |  | 1 |  |  |  |  | 1 | 0.0 % |
| aucinf |  | 4 |  |  |  |  |  |  |  |  |  |  |  | 4 | 100.0 % |
| auclast |  |  | 12 |  |  |  |  |  |  |  |  |  |  | 12 | 100.0 % |
| c0 |  |  |  | 9 |  |  |  |  |  |  |  |  |  | 9 | 100.0 % |
| half_life |  |  |  |  | 2 |  |  |  |  |  |  |  |  | 2 | 100.0 % |
| lambda_z |  |  |  |  |  | 1 |  |  |  |  |  |  |  | 1 | 100.0 % |
| lambda_z_points |  |  |  |  |  |  | 3 |  |  |  |  |  |  | 3 | 100.0 % |
| mrt |  |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 | 0.0 % |
| none |  |  |  |  |  |  |  |  | 12 | 7 |  |  |  | 19 | 63.2 % |
| several |  |  |  |  |  |  |  |  |  | 47 |  |  |  | 47 | 100.0 % |
| tlag |  |  |  |  |  |  |  |  |  |  | 6 | 1 |  | 7 | 85.7 % |
| tmax |  |  |  |  |  |  |  |  |  |  |  | 1 |  | 1 | 100.0 % |
| vz |  |  |  |  |  |  |  |  |  |  |  |  | 5 | 5 | 100.0 % |

### Calibration (all questions; probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 1 | 0.294 | 1.000 |
| [0.3, 0.4) | 10 | 0.369 | 0.400 |
| [0.4, 0.5) | 60 | 0.459 | 0.567 |
| [0.5, 0.6) | 144 | 0.552 | 0.444 |
| [0.6, 0.7) | 126 | 0.648 | 0.571 |
| [0.7, 0.8) | 110 | 0.750 | 0.709 |
| [0.8, 0.9) | 117 | 0.852 | 0.615 |
| [0.9, 1.0] | 216 | 0.947 | 0.921 |

Expected calibration error: 0.090.

## d1-omni-600M, bench, 112 rows (every 8th)

Rows 112, questions 784, device cuda, dtype float16, model load 6.1 s, inference wall 15.3 s (after 2 untimed warm-up rows).
Time per row (one call, seven questions): mean 136.4 ms, median 136.3 ms, p95 149.0 ms. VRAM: nvidia-smi used 641 MiB before load, 1887 after load, 2534 after the run (of 12288); torch peak allocated 1311 MiB.

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 81 | 112 | 72.3 % | 59.8 % | 0.286 |
| auc_method | 62 | 112 | 55.4 % | 83.9 % | 0.047 |
| compare_pair | 58 | 112 | 51.8 % | 90.2 % | 0.107 |
| dose_has_unit | 97 | 112 | 86.6 % | 84.8 % | 0.077 |
| is_not_available | 70 | 112 | 62.5 % | 85.7 % | 0.042 |
| parameter_asked | 56 | 112 | 50.0 % | 42.0 % | 0.234 |
| route | 87 | 112 | 77.7 % | 45.5 % | 0.148 |
| **overall** | 511 | 784 | **65.2 %** | 70.3 % | 0.087 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|
| compare | 5 |  |  | 1 | 4 | 1 | 11 | 45.5 % |
| fit_pk1 |  | 6 |  |  | 1 |  | 7 | 85.7 % |
| fit_pk2 |  | 1 | 9 |  |  |  | 10 | 90.0 % |
| nca |  |  |  | 7 |  |  | 7 | 100.0 % |
| none_needed |  |  | 2 | 10 | 47 | 8 | 67 | 70.1 % |
| simulate |  |  | 2 | 1 |  | 7 | 10 | 70.0 % |

### Confusion: parameter_asked (rows = gold, columns = predicted)

| gold \ pred | adj_r2 | aucinf | auclast | aucpext | c0 | cl | half_life | lambda_z | lambda_z_points | mrt | none | several | tlag | tmax | vz | total | recall |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| adj_r2 |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 | 0.0 % |
| aucinf |  | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  | 4 | 100.0 % |
| auclast |  |  | 6 |  |  |  |  |  |  |  | 2 | 4 |  |  |  | 12 | 50.0 % |
| c0 |  |  |  | 1 | 5 |  |  |  |  |  |  | 2 |  | 1 |  | 9 | 55.6 % |
| half_life |  |  |  |  |  |  |  |  |  |  |  | 2 |  |  |  | 2 | 0.0 % |
| lambda_z |  |  |  |  |  |  |  | 1 |  |  |  |  |  |  |  | 1 | 100.0 % |
| lambda_z_points |  |  |  |  |  |  |  | 2 |  |  | 1 |  |  |  |  | 3 | 0.0 % |
| mrt |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |  | 1 | 100.0 % |
| none |  |  |  |  |  |  |  |  |  |  | 8 | 11 |  |  |  | 19 | 42.1 % |
| several |  |  |  | 5 | 4 | 5 |  | 2 |  |  | 8 | 21 |  | 2 |  | 47 | 44.7 % |
| tlag |  |  |  |  |  |  |  |  |  |  |  | 3 | 4 |  |  | 7 | 57.1 % |
| tmax |  |  |  |  |  |  |  |  |  |  |  |  |  | 1 |  | 1 | 100.0 % |
| vz |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 5 | 5 | 100.0 % |

### Calibration (all questions; probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 23 | 0.164 | 0.348 |
| [0.2, 0.3) | 66 | 0.254 | 0.485 |
| [0.3, 0.4) | 79 | 0.351 | 0.557 |
| [0.4, 0.5) | 97 | 0.451 | 0.577 |
| [0.5, 0.6) | 177 | 0.547 | 0.576 |
| [0.6, 0.7) | 114 | 0.643 | 0.605 |
| [0.7, 0.8) | 69 | 0.742 | 0.754 |
| [0.8, 0.9) | 56 | 0.845 | 0.946 |
| [0.9, 1.0] | 103 | 0.962 | 0.922 |

Expected calibration error: 0.087.

## d1-omni-600M, bench

Rows 900, questions 6300, device cuda, dtype float16, model load 6.3 s, inference wall 125.8 s (after 2 untimed warm-up rows).
Time per row (one call, seven questions): mean 139.6 ms, median 139.5 ms, p95 149.7 ms. VRAM: nvidia-smi used 605 MiB before load, 1887 after load, 2586 after the run (of 12288); torch peak allocated 1317 MiB.

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 597 | 900 | 66.3 % | 58.3 % | 0.230 |
| auc_method | 529 | 900 | 58.8 % | 83.3 % | 0.072 |
| compare_pair | 410 | 900 | 45.6 % | 91.7 % | 0.171 |
| dose_has_unit | 771 | 900 | 85.7 % | 84.0 % | 0.039 |
| is_not_available | 517 | 900 | 57.4 % | 91.7 % | 0.064 |
| parameter_asked | 454 | 900 | 50.4 % | 49.0 % | 0.221 |
| route | 639 | 900 | 71.0 % | 49.8 % | 0.067 |
| **overall** | 3917 | 6300 | **62.2 %** | 72.5 % | 0.076 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|
| compare | 24 |  | 1 | 10 | 34 | 6 | 75 | 32.0 % |
| fit_pk1 |  | 62 | 2 |  | 7 | 4 | 75 | 82.7 % |
| fit_pk2 |  | 14 | 57 | 1 |  | 3 | 75 | 76.0 % |
| nca |  | 14 |  | 60 | 1 |  | 75 | 80.0 % |
| none_needed |  | 8 | 20 | 83 | 337 | 77 | 525 | 64.2 % |
| simulate |  | 4 | 9 | 2 | 3 | 57 | 75 | 76.0 % |

### Confusion: parameter_asked (rows = gold, columns = predicted)

| gold \ pred | adj_r2 | aucinf | auclast | aucpext | c0 | cl | cmax | half_life | lambda_z | lambda_z_points | mrt | none | several | tlag | tmax | vz | total | recall |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| adj_r2 | 2 |  |  |  |  |  |  |  |  |  |  |  | 10 |  |  |  | 12 | 16.7 % |
| aucinf |  | 21 |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 21 | 100.0 % |
| auclast |  |  | 33 |  |  |  |  |  |  |  |  | 26 | 30 |  |  |  | 89 | 37.1 % |
| aucpext |  |  |  | 6 |  |  |  |  |  |  |  |  | 3 |  |  |  | 9 | 66.7 % |
| c0 |  |  | 1 | 6 | 32 |  |  |  |  |  |  | 2 | 6 |  | 3 |  | 50 | 64.0 % |
| cl |  |  |  |  |  |  |  |  |  |  |  | 12 | 1 |  |  |  | 13 | 0.0 % |
| cmax |  |  |  |  |  |  | 7 |  |  |  |  |  |  |  |  |  | 7 | 100.0 % |
| half_life |  |  |  |  |  |  |  |  | 1 |  |  |  | 22 |  |  |  | 23 | 0.0 % |
| lambda_z |  |  |  |  |  |  |  |  | 13 |  |  |  |  |  |  |  | 13 | 100.0 % |
| lambda_z_points |  |  |  |  |  |  |  |  | 12 |  |  | 2 | 5 |  |  |  | 19 | 0.0 % |
| mrt |  |  |  |  |  |  |  |  |  |  | 9 | 1 | 1 |  |  |  | 11 | 81.8 % |
| none |  |  |  |  |  |  |  |  |  |  |  | 56 | 94 |  |  |  | 150 | 37.3 % |
| several |  |  |  | 33 | 11 | 12 | 10 | 3 | 36 | 8 |  | 44 | 241 |  | 43 |  | 441 | 54.6 % |
| tlag |  |  |  |  |  |  |  |  |  |  |  | 2 | 6 | 20 |  |  | 28 | 71.4 % |
| tmax |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 4 |  | 4 | 100.0 % |
| vz |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 10 | 10 | 100.0 % |

### Calibration (all questions; probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 2 | 0.098 | 1.000 |
| [0.1, 0.2) | 216 | 0.170 | 0.519 |
| [0.2, 0.3) | 530 | 0.253 | 0.470 |
| [0.3, 0.4) | 673 | 0.354 | 0.510 |
| [0.4, 0.5) | 799 | 0.449 | 0.542 |
| [0.5, 0.6) | 1363 | 0.548 | 0.532 |
| [0.6, 0.7) | 992 | 0.643 | 0.577 |
| [0.7, 0.8) | 550 | 0.744 | 0.749 |
| [0.8, 0.9) | 405 | 0.848 | 0.852 |
| [0.9, 1.0] | 770 | 0.960 | 0.940 |

Expected calibration error: 0.076.

## d1-3B, heldout, first 10 rows

Rows 10, questions 70, device cpu, dtype float32, model load 11.9 s, inference wall 141.4 s (after 1 untimed warm-up rows).
Time per row (one call, seven questions): mean 14144.0 ms, median 14143.4 ms, p95 14398.0 ms. VRAM: none (cpu).

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 10 | 10 | 100.0 % | 60.0 % | 0.269 |
| auc_method | 8 | 10 | 80.0 % | 80.0 % | 0.333 |
| compare_pair | 1 | 10 | 10.0 % | 100.0 % | 0.549 |
| dose_has_unit | 9 | 10 | 90.0 % | 90.0 % | 0.108 |
| is_not_available | 3 | 10 | 30.0 % | 90.0 % | 0.403 |
| parameter_asked | 9 | 10 | 90.0 % | 60.0 % | 0.224 |
| route | 6 | 10 | 60.0 % | 70.0 % | 0.124 |
| **overall** | 46 | 70 | **65.7 %** | 78.6 % | 0.104 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | fit_pk1 | nca | none_needed | total | recall |
|---|---|---|---|---|---|
| fit_pk1 | 2 |  |  | 2 | 100.0 % |
| nca |  | 2 |  | 2 | 100.0 % |
| none_needed |  |  | 6 | 6 | 100.0 % |

### Confusion: parameter_asked (rows = gold, columns = predicted)

| gold \ pred | c0 | lambda_z | none | several | total | recall |
|---|---|---|---|---|---|---|
| c0 | 1 |  |  |  | 1 | 100.0 % |
| lambda_z |  | 1 |  |  | 1 | 100.0 % |
| none |  |  | 1 | 1 | 2 | 50.0 % |
| several |  |  |  | 6 | 6 | 100.0 % |

### Calibration (all questions; probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 0 | - | - |
| [0.3, 0.4) | 0 | - | - |
| [0.4, 0.5) | 6 | 0.475 | 0.333 |
| [0.5, 0.6) | 14 | 0.550 | 0.500 |
| [0.6, 0.7) | 12 | 0.640 | 0.667 |
| [0.7, 0.8) | 10 | 0.744 | 0.600 |
| [0.8, 0.9) | 12 | 0.844 | 0.583 |
| [0.9, 1.0] | 16 | 0.946 | 1.000 |

Expected calibration error: 0.104.

## d1-omni-600M, heldout, first 20 rows

Rows 20, questions 140, device cuda, dtype float16, model load 5.9 s, inference wall 2.6 s (after 2 untimed warm-up rows).
Time per row (one call, seven questions): mean 131.9 ms, median 131.1 ms, p95 139.0 ms. VRAM: nvidia-smi used 649 MiB before load, 1862 after load, 2442 after the run (of 12288); torch peak allocated 1286 MiB.

### Accuracy per question

| question | correct | total | accuracy | always-majority | ECE |
|---|---|---|---|---|---|
| analysis | 14 | 20 | 70.0 % | 50.0 % | 0.288 |
| auc_method | 16 | 20 | 80.0 % | 80.0 % | 0.264 |
| compare_pair | 9 | 20 | 45.0 % | 95.0 % | 0.180 |
| dose_has_unit | 17 | 20 | 85.0 % | 85.0 % | 0.108 |
| is_not_available | 11 | 20 | 55.0 % | 90.0 % | 0.111 |
| parameter_asked | 10 | 20 | 50.0 % | 55.0 % | 0.207 |
| route | 16 | 20 | 80.0 % | 40.0 % | 0.145 |
| **overall** | 93 | 140 | **66.4 %** | 70.7 % | 0.111 |

### Confusion: analysis (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|
| compare | 1 |  |  |  |  |  | 1 | 100.0 % |
| fit_pk1 |  | 1 |  |  | 1 |  | 2 | 50.0 % |
| fit_pk2 |  | 1 | 1 |  |  |  | 2 | 50.0 % |
| nca |  |  |  | 3 |  |  | 3 | 100.0 % |
| none_needed |  | 1 |  | 2 | 7 |  | 10 | 70.0 % |
| simulate |  |  | 1 |  |  | 1 | 2 | 50.0 % |

### Confusion: parameter_asked (rows = gold, columns = predicted)

| gold \ pred | auclast | c0 | lambda_z | lambda_z_points | none | several | tlag | tmax | total | recall |
|---|---|---|---|---|---|---|---|---|---|---|
| auclast | 1 |  |  |  | 1 |  |  |  | 2 | 50.0 % |
| c0 |  |  |  |  |  | 1 |  |  | 1 | 0.0 % |
| lambda_z |  |  | 1 |  |  |  |  |  | 1 | 100.0 % |
| none |  |  |  |  | 2 | 2 |  |  | 4 | 50.0 % |
| several |  |  | 1 | 1 | 2 | 5 |  | 2 | 11 | 45.5 % |
| tlag |  |  |  |  |  |  | 1 |  | 1 | 100.0 % |

### Calibration (all questions; probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 5 | 0.150 | 0.400 |
| [0.2, 0.3) | 10 | 0.248 | 0.400 |
| [0.3, 0.4) | 13 | 0.358 | 0.615 |
| [0.4, 0.5) | 19 | 0.454 | 0.684 |
| [0.5, 0.6) | 26 | 0.559 | 0.538 |
| [0.6, 0.7) | 27 | 0.639 | 0.667 |
| [0.7, 0.8) | 9 | 0.735 | 0.444 |
| [0.8, 0.9) | 11 | 0.866 | 0.909 |
| [0.9, 1.0] | 20 | 0.963 | 1.000 |

Expected calibration error: 0.111.

## What was run, and what failed

Commands (from `agent/`, with `.venv-d1`, pinned in `decision/requirements-d1.txt`; python 3.12.10, torch 2.14.1+cu130, transformers 5.19.0; models `LiquidAI/d1-omni-600M` and `LiquidAI/d1-3B`, remote code revisions as downloaded on 2026-10-09; GPU RTX 3060 12 GB, about 2 GB used by the desktop before the runs):

```
python decision/zero_shot_d1.py --model d1-omni-600M --split heldout --limit 20                       # smoke, cuda, float16
python decision/zero_shot_d1.py --model d1-omni-600M --split heldout                                  # 720 rows
python decision/zero_shot_d1.py --model d1-omni-600M --split bench                                    # 900 rows
python decision/zero_shot_d1.py --model d1-3B --split heldout --limit 20                              # smoke on cuda: FAILED, see below
python decision/zero_shot_d1.py --model d1-3B --split heldout --limit 10 --device cpu --warmup 1      # smoke, cpu
python decision/zero_shot_d1.py --model d1-3B --split heldout --limit 120 --stride 6 --device cpu --warmup 1
python decision/zero_shot_d1.py --model d1-3B --split bench --limit 112 --stride 8 --device cpu --warmup 1
python decision/zero_shot_d1.py --model d1-omni-600M --split heldout --limit 120 --stride 6           # same rows as the 3B run
python decision/zero_shot_d1.py --model d1-omni-600M --split bench --limit 112 --stride 8
```

`--stride K` (every K-th row) is an addition to the requested flags: the jsonl files are ordered by exercise, so the first N rows would cover only 3 or 4 exercises; a stride spreads the CPU runs over all 20 (held-out) or 25 (bench) exercises. The 600M was re-run on the same strided rows so that the two models can be compared on identical rows.

**d1-3B does not run on the GPU here.** The weights load on cuda in bfloat16 (nvidia-smi: 6761 MiB used of 12288 after load, torch allocated 5969 MiB; they fit), and the first `system_one` call fails in the model's own remote code (`hybrid.py`, `_own`, line 174, the fused path taken for a CUDA half-precision tensor on compute capability 8.x):

```
torch.ops.aten._flash_attention_forward(...)
RuntimeError: USE_FLASH_ATTENTION was not enabled for build.
```

The RTX 3060 (compute capability 8.6) has the hardware for it; what is missing is the flash-attention kernel in the PyTorch Windows wheel (`torch 2.14.1+cu130`, `torch.backends.cuda.flash_sdp_enabled()` is True but the op is not compiled in). The code has a non-fused path (`_explicit`) but it is only chosen on CPU or in float32, so no workaround was tried on the GPU (no patch of the remote code, no float32 on cuda): the failure is documented and the 3B was run on CPU, in float32, as the model card does on CPU. Next options, not done: Linux or WSL with a PyTorch build that includes flash attention (the same environment step 3 needs for Unsloth), or a PyTorch build for Windows with `USE_FLASH_ATTENTION`.

**Consequences for the numbers.** The 3B figures are on 120 held-out rows and 112 bench rows (a subset, about 14.2 s per row on 12 CPU threads, 28 and 26 minutes), not on the full sets; the 3B and 600M times are on different devices and are not a speed comparison. The 600M on the same subsets is in the table above.
