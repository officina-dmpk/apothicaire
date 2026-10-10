# Relevance ablation on heldout_both.jsonl (593 rows), model qwen35-0.8b-d01-v2-adapters

`decision/ablation.py`; none = the rows as they are, random_conc = concentrations of the digest replaced by random values of the same magnitude, no_table = the data key removed from the state. Gold unchanged (no gold label is computed from a concentration value).

| mode | decisions right | all 20 right on a row | decisions that flip against `none` |
|---|---|---|---|
| none | 11643 / 11860 = 98.17 % | 400 / 593 | - |
| random_conc | 11648 / 11860 = 98.21 % | 406 / 593 | 18 / 11860 |
| no_table | 11635 / 11860 = 98.10 % | 394 / 593 | 74 / 11860 |

Per question: accuracy without ablation, accuracy after, flips (of 593), mean absolute change of the probability of the original label.

| question | none | random_conc | flips | mean dp | no_table | flips | mean dp |
|---|---|---|---|---|---|---|---|
| analysis | 95.1 % | 94.9 % | 9 | 0.0092 | 92.9 % | 17 | 0.0329 |
| asked_adj_r2 | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_aucinf | 99.8 % | 100.0 % | 1 | 0.0010 | 100.0 % | 1 | 0.0019 |
| asked_auclast | 97.0 % | 97.3 % | 2 | 0.0026 | 97.8 % | 11 | 0.0183 |
| asked_aucpext | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_c0 | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_cl | 97.5 % | 97.5 % | 0 | 0.0003 | 97.5 % | 0 | 0.0006 |
| asked_cmax | 97.6 % | 97.6 % | 0 | 0.0000 | 100.0 % | 14 | 0.0236 |
| asked_half_life | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_lambda_z | 98.8 % | 98.8 % | 0 | 0.0001 | 96.5 % | 14 | 0.0207 |
| asked_lambda_z_points | 97.5 % | 97.5 % | 0 | 0.0000 | 97.5 % | 0 | 0.0000 |
| asked_mrt | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0002 |
| asked_tlag | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_tmax | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_vz | 96.0 % | 96.0 % | 0 | 0.0000 | 96.0 % | 0 | 0.0002 |
| auc_method | 90.7 % | 91.1 % | 3 | 0.0043 | 91.6 % | 9 | 0.0167 |
| compare_pair | 98.0 % | 98.0 % | 0 | 0.0007 | 98.0 % | 0 | 0.0029 |
| dose_has_unit | 100.0 % | 100.0 % | 0 | 0.0000 | 99.3 % | 4 | 0.0060 |
| is_not_available | 96.3 % | 96.5 % | 1 | 0.0013 | 96.0 % | 2 | 0.0037 |
| route | 99.2 % | 99.2 % | 2 | 0.0024 | 99.2 % | 2 | 0.0040 |
