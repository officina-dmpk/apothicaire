### Accuracy per question (825 rows)

| question | model | best constant | reviewer's rules |
|---|---|---|---|
| analysis | 95.2 % | 46.7 % | 77.0 % |
| route | 99.5 % | 49.2 % | 30.9 % |
| auc_method | 91.5 % | 80.0 % | 84.7 % |
| dose_has_unit | 100.0 % | 79.2 % | 88.0 % |
| is_not_available | 95.8 % | 93.3 % | 94.9 % |
| compare_pair | 98.5 % | 86.7 % | 95.5 % |
| `asked_<parameter>` (14 questions pooled) | 98.9 % | 91.3 % | 91.3 % |
| macro-average of the seven | 97.0 % | 75.2 % | 80.3 % |
| **all 20, per decision** | 98.2 % | 85.6 % | 87.4 % |

### Complete vectors

All 20 labels right: model 568 / 825 = 68.8 %; reviewer's rules 22 / 825 = 2.7 %.

### All 20 questions

| question | model | best constant | reviewer's rules |
|---|---|---|---|
| analysis | 95.2 % | 46.7 % | 77.0 % |
| asked_adj_r2 | 100.0 % | 93.9 % | 93.9 % |
| asked_aucinf | 99.8 % | 88.5 % | 88.5 % |
| asked_auclast | 96.7 % | 84.6 % | 84.6 % |
| asked_aucpext | 100.0 % | 96.2 % | 96.2 % |
| asked_c0 | 100.0 % | 95.6 % | 95.6 % |
| asked_cl | 98.4 % | 92.8 % | 92.8 % |
| asked_cmax | 97.2 % | 84.4 % | 84.4 % |
| asked_half_life | 100.0 % | 82.7 % | 82.7 % |
| asked_lambda_z | 98.5 % | 95.2 % | 95.2 % |
| asked_lambda_z_points | 97.9 % | 95.0 % | 95.0 % |
| asked_mrt | 100.0 % | 89.0 % | 89.0 % |
| asked_tlag | 100.0 % | 97.6 % | 97.6 % |
| asked_tmax | 100.0 % | 91.2 % | 91.2 % |
| asked_vz | 95.4 % | 91.0 % | 91.0 % |
| auc_method | 91.5 % | 80.0 % | 84.7 % |
| compare_pair | 98.5 % | 86.7 % | 95.5 % |
| dose_has_unit | 100.0 % | 79.2 % | 88.0 % |
| is_not_available | 95.8 % | 93.3 % | 94.9 % |
| route | 99.5 % | 49.2 % | 30.9 % |
| **all 20, per decision** | 98.2 % | 85.6 % | 87.4 % |
