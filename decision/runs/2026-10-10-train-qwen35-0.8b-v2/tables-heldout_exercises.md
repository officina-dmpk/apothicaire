### Accuracy per question (920 rows)

| question | model | best constant | reviewer's rules |
|---|---|---|---|
| analysis | 99.1 % | 45.7 % | 76.7 % |
| route | 100.0 % | 44.3 % | 82.3 % |
| auc_method | 98.4 % | 78.3 % | 80.5 % |
| dose_has_unit | 99.6 % | 81.4 % | 89.7 % |
| is_not_available | 93.5 % | 93.5 % | 97.9 % |
| compare_pair | 99.2 % | 87.0 % | 91.8 % |
| `asked_<parameter>` (14 questions pooled) | 100.0 % | 91.0 % | 91.0 % |
| macro-average of the seven | 98.5 % | 74.4 % | 87.1 % |
| **all 20, per decision** | 99.5 % | 85.2 % | 89.7 % |

### Complete vectors

All 20 labels right: model 828 / 920 = 90.0 %; reviewer's rules 98 / 920 = 10.7 %.

### All 20 questions

| question | model | best constant | reviewer's rules |
|---|---|---|---|
| analysis | 99.1 % | 45.7 % | 76.7 % |
| asked_adj_r2 | 100.0 % | 93.8 % | 93.8 % |
| asked_aucinf | 100.0 % | 91.3 % | 91.3 % |
| asked_auclast | 100.0 % | 82.2 % | 82.2 % |
| asked_aucpext | 100.0 % | 94.1 % | 94.1 % |
| asked_c0 | 100.0 % | 95.2 % | 95.2 % |
| asked_cl | 100.0 % | 90.3 % | 90.3 % |
| asked_cmax | 100.0 % | 86.8 % | 86.8 % |
| asked_half_life | 100.0 % | 87.5 % | 87.5 % |
| asked_lambda_z | 100.0 % | 92.1 % | 92.1 % |
| asked_lambda_z_points | 100.0 % | 95.4 % | 95.4 % |
| asked_mrt | 100.0 % | 92.4 % | 92.4 % |
| asked_tlag | 100.0 % | 96.3 % | 96.3 % |
| asked_tmax | 100.0 % | 87.6 % | 87.6 % |
| asked_vz | 100.0 % | 89.0 % | 89.0 % |
| auc_method | 98.4 % | 78.3 % | 80.5 % |
| compare_pair | 99.2 % | 87.0 % | 91.8 % |
| dose_has_unit | 99.6 % | 81.4 % | 89.7 % |
| is_not_available | 93.5 % | 93.5 % | 97.9 % |
| route | 100.0 % | 44.3 % | 82.3 % |
| **all 20, per decision** | 99.5 % | 85.2 % | 89.7 % |
