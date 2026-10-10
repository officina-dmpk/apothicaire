### Accuracy per question (593 rows)

| question | model | best constant | reviewer's rules |
|---|---|---|---|
| analysis | 95.3 % | 46.0 % | 78.6 % |
| route | 98.3 % | 41.5 % | 40.3 % |
| auc_method | 88.0 % | 79.8 % | 85.7 % |
| dose_has_unit | 100.0 % | 78.4 % | 90.1 % |
| is_not_available | 94.4 % | 94.4 % | 95.3 % |
| compare_pair | 97.0 % | 86.5 % | 94.9 % |
| `asked_<parameter>` (14 questions pooled) | 98.8 % | 91.7 % | 91.7 % |
| macro-average of the seven | 96.0 % | 74.1 % | 82.4 % |
| **all 20, per decision** | 97.8 % | 85.6 % | 88.5 % |

### Complete vectors

All 20 labels right: model 362 / 593 = 61.0 %; reviewer's rules 33 / 593 = 5.6 %.

### All 20 questions

| question | model | best constant | reviewer's rules |
|---|---|---|---|
| analysis | 95.3 % | 46.0 % | 78.6 % |
| asked_adj_r2 | 100.0 % | 93.9 % | 93.9 % |
| asked_aucinf | 100.0 % | 90.4 % | 90.4 % |
| asked_auclast | 97.0 % | 86.7 % | 86.7 % |
| asked_aucpext | 99.8 % | 96.3 % | 96.3 % |
| asked_c0 | 100.0 % | 95.4 % | 95.4 % |
| asked_cl | 97.5 % | 93.1 % | 93.1 % |
| asked_cmax | 97.6 % | 85.7 % | 85.7 % |
| asked_half_life | 100.0 % | 82.1 % | 82.1 % |
| asked_lambda_z | 98.3 % | 94.3 % | 94.3 % |
| asked_lambda_z_points | 97.5 % | 93.9 % | 93.9 % |
| asked_mrt | 99.3 % | 89.7 % | 89.7 % |
| asked_tlag | 100.0 % | 98.5 % | 98.5 % |
| asked_tmax | 100.0 % | 92.1 % | 92.1 % |
| asked_vz | 96.0 % | 92.4 % | 92.4 % |
| auc_method | 88.0 % | 79.8 % | 85.7 % |
| compare_pair | 97.0 % | 86.5 % | 94.9 % |
| dose_has_unit | 100.0 % | 78.4 % | 90.1 % |
| is_not_available | 94.4 % | 94.4 % | 95.3 % |
| route | 98.3 % | 41.5 % | 40.3 % |
| **all 20, per decision** | 97.8 % | 85.6 % | 88.5 % |
