# Relevance ablation on heldout_both.jsonl (593 rows), model qwen35-0.8b-d01-v2

`decision/ablation.py`; none = the rows as they are, random_conc = concentrations of the digest replaced by random values of the same magnitude, no_table = the data key removed from the state. Gold unchanged (no gold label is computed from a concentration value).

| mode | decisions right | all 20 right on a row | decisions that flip against `none` |
|---|---|---|---|
| none | 11599 / 11860 = 97.80 % | 362 / 593 | - |
| random_conc | 11602 / 11860 = 97.82 % | 367 / 593 | 17 / 11860 |
| no_table | 11561 / 11860 = 97.48 % | 347 / 593 | 88 / 11860 |

Per question: accuracy without ablation, accuracy after, flips (of 593), mean absolute change of the probability of the original label.

| question | none | random_conc | flips | mean dp | no_table | flips | mean dp |
|---|---|---|---|---|---|---|---|
| analysis | 95.3 % | 95.1 % | 7 | 0.0097 | 90.1 % | 33 | 0.0567 |
| asked_adj_r2 | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_aucinf | 100.0 % | 100.0 % | 0 | 0.0003 | 100.0 % | 0 | 0.0011 |
| asked_auclast | 97.0 % | 97.0 % | 0 | 0.0000 | 98.0 % | 6 | 0.0093 |
| asked_aucpext | 99.8 % | 99.8 % | 0 | 0.0009 | 99.5 % | 2 | 0.0029 |
| asked_c0 | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_cl | 97.5 % | 97.5 % | 0 | 0.0003 | 97.5 % | 0 | 0.0008 |
| asked_cmax | 97.6 % | 97.6 % | 0 | 0.0002 | 98.8 % | 21 | 0.0338 |
| asked_half_life | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_lambda_z | 98.3 % | 98.8 % | 3 | 0.0019 | 98.8 % | 3 | 0.0033 |
| asked_lambda_z_points | 97.5 % | 97.5 % | 0 | 0.0000 | 97.5 % | 0 | 0.0000 |
| asked_mrt | 99.3 % | 99.0 % | 2 | 0.0038 | 97.0 % | 14 | 0.0207 |
| asked_tlag | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_tmax | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_vz | 96.0 % | 96.0 % | 0 | 0.0003 | 95.8 % | 1 | 0.0056 |
| auc_method | 88.0 % | 88.0 % | 0 | 0.0015 | 88.0 % | 0 | 0.0060 |
| compare_pair | 97.0 % | 97.1 % | 3 | 0.0009 | 96.6 % | 4 | 0.0029 |
| dose_has_unit | 100.0 % | 100.0 % | 0 | 0.0000 | 99.7 % | 2 | 0.0034 |
| is_not_available | 94.4 % | 94.4 % | 0 | 0.0000 | 94.4 % | 0 | 0.0000 |
| route | 98.3 % | 98.7 % | 2 | 0.0008 | 98.0 % | 2 | 0.0080 |
