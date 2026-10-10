### Accuracy per question (74 rows)

| question | model | best constant | reviewer's rules |
|---|---|---|---|
| analysis | 82.4 % | 60.8 % | 77.0 % |
| route | 90.5 % | 54.1 % | 87.8 % |
| auc_method | 54.1 % | 77.0 % | 74.3 % |
| dose_has_unit | 97.3 % | 93.2 % | 100.0 % |
| is_not_available | 85.1 % | 85.1 % | 91.9 % |
| compare_pair | 97.3 % | 94.6 % | 97.3 % |
| `asked_<parameter>` (14 questions pooled) | 98.2 % | 90.4 % | 90.4 % |
| macro-average of the seven | 86.4 % | 79.3 % | 88.4 % |
| **all 20, per decision** | 94.1 % | 86.6 % | 89.7 % |

### Complete vectors

All 20 labels right: model 20 / 74 = 27.0 %; reviewer's rules 0 / 74 = 0.0 %.

### All 20 questions

| question | model | best constant | reviewer's rules |
|---|---|---|---|
| analysis | 82.4 % | 60.8 % | 77.0 % |
| asked_adj_r2 | 100.0 % | 98.6 % | 98.6 % |
| asked_aucinf | 90.5 % | 91.9 % | 91.9 % |
| asked_auclast | 90.5 % | 73.0 % | 73.0 % |
| asked_aucpext | 97.3 % | 95.9 % | 95.9 % |
| asked_c0 | 100.0 % | 95.9 % | 95.9 % |
| asked_cl | 98.6 % | 87.8 % | 87.8 % |
| asked_cmax | 98.6 % | 70.3 % | 70.3 % |
| asked_half_life | 100.0 % | 87.8 % | 87.8 % |
| asked_lambda_z | 100.0 % | 98.6 % | 98.6 % |
| asked_lambda_z_points | 100.0 % | 97.3 % | 97.3 % |
| asked_mrt | 100.0 % | 95.9 % | 95.9 % |
| asked_tlag | 100.0 % | 94.6 % | 94.6 % |
| asked_tmax | 100.0 % | 90.5 % | 90.5 % |
| asked_vz | 98.6 % | 87.8 % | 87.8 % |
| auc_method | 54.1 % | 77.0 % | 74.3 % |
| compare_pair | 97.3 % | 94.6 % | 97.3 % |
| dose_has_unit | 97.3 % | 93.2 % | 100.0 % |
| is_not_available | 85.1 % | 85.1 % | 91.9 % |
| route | 90.5 % | 54.1 % | 87.8 % |
| **all 20, per decision** | 94.1 % | 86.6 % | 89.7 % |
