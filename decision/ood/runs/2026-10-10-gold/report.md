# Out-of-distribution requests: decider `gold`, 2026-10-10

`decision/eval_ood.py`; 74 requests converted from `decision/ood/requests.jsonl` (schema report: `decision/ood/schema_report.md`).

## Scoring on the rows

74 rows, 1480 decisions: **100.0 %** correct overall; 74 of 74 rows have all their decisions right (100.0 %). Always-majority on these rows: 86.6 %; majority learned on train.jsonl: 81.4 %.

### Accuracy per question

| question | correct | total | accuracy | always-majority (these rows) | majority (train.jsonl) |
|---|---|---|---|---|---|
| analysis | 74 | 74 | 100.0 % | 60.8 % | 21.6 % |
| asked_adj_r2 | 74 | 74 | 100.0 % | 98.6 % | 98.6 % |
| asked_aucinf | 74 | 74 | 100.0 % | 91.9 % | 91.9 % |
| asked_auclast | 74 | 74 | 100.0 % | 73.0 % | 73.0 % |
| asked_aucpext | 74 | 74 | 100.0 % | 95.9 % | 95.9 % |
| asked_c0 | 74 | 74 | 100.0 % | 95.9 % | 95.9 % |
| asked_cl | 74 | 74 | 100.0 % | 87.8 % | 87.8 % |
| asked_cmax | 74 | 74 | 100.0 % | 70.3 % | 70.3 % |
| asked_half_life | 74 | 74 | 100.0 % | 87.8 % | 87.8 % |
| asked_lambda_z | 74 | 74 | 100.0 % | 98.6 % | 98.6 % |
| asked_lambda_z_points | 74 | 74 | 100.0 % | 97.3 % | 97.3 % |
| asked_mrt | 74 | 74 | 100.0 % | 95.9 % | 95.9 % |
| asked_tlag | 74 | 74 | 100.0 % | 94.6 % | 94.6 % |
| asked_tmax | 74 | 74 | 100.0 % | 90.5 % | 90.5 % |
| asked_vz | 74 | 74 | 100.0 % | 87.8 % | 87.8 % |
| auc_method | 74 | 74 | 100.0 % | 77.0 % | 12.2 % |
| compare_pair | 74 | 74 | 100.0 % | 94.6 % | 94.6 % |
| dose_has_unit | 74 | 74 | 100.0 % | 93.2 % | 93.2 % |
| is_not_available | 74 | 74 | 100.0 % | 85.1 % | 85.1 % |
| route | 74 | 74 | 100.0 % | 54.1 % | 54.1 % |
| **overall** | 1480 | 1480 | **100.0 %** | 86.6 % | 81.4 % |

### Confusions (wrong cells only: gold -> predicted, count)

- `analysis`: no error.
- `route`: no error.
- `auc_method`: no error.
- `compare_pair`: no error.
- `is_not_available`: no error.
- `dose_has_unit`: no error.
- `asked_<parameter>` (14 questions): 0 parameters asked and missed (of 99 asked), 0 parameters predicted asked that were not.

### Accuracy per tag (which kinds of hard requests break)

| tag | rows | decisions correct | accuracy | rows all right |
|---|---|---|---|---|
| abbreviation | 17 | 340/340 | 100.0 % | 100.0 % |
| bioequivalence | 1 | 20/20 | 100.0 % | 100.0 % |
| blq | 4 | 80/80 | 100.0 % | 100.0 % |
| by-id | 2 | 40/40 | 100.0 % | 100.0 % |
| c0 | 1 | 20/20 | 100.0 % | 100.0 % |
| colloquial | 6 | 120/120 | 100.0 % | 100.0 % |
| compare | 8 | 160/160 | 100.0 % | 100.0 % |
| dose-unit-g | 1 | 20/20 | 100.0 % | 100.0 % |
| dose-unit-mcg | 1 | 20/20 | 100.0 % | 100.0 % |
| dose-unit-mg | 1 | 20/20 | 100.0 % | 100.0 % |
| dose-unit-micro | 9 | 180/180 | 100.0 % | 100.0 % |
| dose-without-unit | 1 | 20/20 | 100.0 % | 100.0 % |
| duration-unit-mismatch | 2 | 40/40 | 100.0 % | 100.0 % |
| duration-word | 1 | 20/20 | 100.0 % | 100.0 % |
| english-term | 1 | 20/20 | 100.0 % | 100.0 % |
| fit | 4 | 80/80 | 100.0 % | 100.0 % |
| follow-up | 4 | 80/80 | 100.0 % | 100.0 % |
| infusion | 7 | 140/140 | 100.0 % | 100.0 % |
| invented | 16 | 320/320 | 100.0 % | 100.0 % |
| iv-explicit | 1 | 20/20 | 100.0 % | 100.0 % |
| language-mix | 2 | 40/40 | 100.0 % | 100.0 % |
| latin-route | 3 | 60/60 | 100.0 % | 100.0 % |
| method-explicit | 2 | 40/40 | 100.0 % | 100.0 % |
| multi-subject | 1 | 20/20 | 100.0 % | 100.0 % |
| multiple-dose | 1 | 20/20 | 100.0 % | 100.0 % |
| no-dose | 1 | 20/20 | 100.0 % | 100.0 % |
| no-parameter | 1 | 20/20 | 100.0 % | 100.0 % |
| no-prior-analysis | 1 | 20/20 | 100.0 % | 100.0 % |
| non-auc-parameter | 1 | 20/20 | 100.0 % | 100.0 % |
| oral | 1 | 20/20 | 100.0 % | 100.0 % |
| out-of-scope | 4 | 80/80 | 100.0 % | 100.0 % |
| parameter-not-for-route | 5 | 100/100 | 100.0 % | 100.0 % |
| parameter-not-in-schema | 2 | 40/40 | 100.0 % | 100.0 % |
| plain | 2 | 40/40 | 100.0 % | 100.0 % |
| population | 1 | 20/20 | 100.0 % | 100.0 % |
| recall | 1 | 20/20 | 100.0 % | 100.0 % |
| rerun | 4 | 80/80 | 100.0 % | 100.0 % |
| route-implied | 5 | 100/100 | 100.0 % | 100.0 % |
| route-missing | 1 | 20/20 | 100.0 % | 100.0 % |
| route-stated | 8 | 160/160 | 100.0 % | 100.0 % |
| simulate | 1 | 20/20 | 100.0 % | 100.0 % |
| steady-state | 1 | 20/20 | 100.0 % | 100.0 % |
| terminology-mismatch | 2 | 40/40 | 100.0 % | 100.0 % |
| tlag | 1 | 20/20 | 100.0 % | 100.0 % |
| two-compartments | 2 | 40/40 | 100.0 % | 100.0 % |
| two-requests-in-one-sentence | 2 | 40/40 | 100.0 % | 100.0 % |
| typo | 2 | 40/40 | 100.0 % | 100.0 % |
| unicode | 1 | 20/20 | 100.0 % | 100.0 % |
| unit-conversion-in-text | 1 | 20/20 | 100.0 % | 100.0 % |
| unit-in-text | 5 | 100/100 | 100.0 % | 100.0 % |
| unit-variety | 1 | 20/20 | 100.0 % | 100.0 % |
| unrecognized-unit | 1 | 20/20 | 100.0 % | 100.0 % |
| urine | 1 | 20/20 | 100.0 % | 100.0 % |

Tags that broke (share of fully correct rows below the overall share): none.

### Calibration (probability of the chosen label vs observed accuracy)

The decider gives labels without probabilities: no calibration table.

### Wrong decisions (0)

None.

## Harness run

74 requests, one fresh Caladrius session each: **41 answers with values, 33 refusals or questions back**, 0 errors, 0 skipped (prior analyses that cannot be replayed).

| kind of answer | count |
|---|---|
| answer | 41 |
| refusal:ask | 13 |
| refusal:no-analysis | 1 |
| refusal:not-available | 11 |
| refusal:not-wired | 5 |
| refusal:which-pair | 3 |

No oracle applies to free requests (bench/score.py reads the scripted turns). Instead:

- answered where the gold decisions expect a refusal or a question back (the dangerous direction): 0
- refused or asked where the gold decisions expect an answer: 12 (ood-008, ood-010, ood-011, ood-013, ood-030, ood-037, ood-043, ood-055, ood-058, ood-062, ood-070, ood-071)
- rows whose state, rebuilt by the harness, differs from the scored row: 0
- decisions that came back outside the offered options: 0

## What a human must read (12 of 74 requests)

Wrong decisions in the run, answers that contradict the gold decisions, errors, and the requests of the tags that broke (at most 6 per tag). Every other answer is in `answers.jsonl`; a correct decision does not make a correct answer, so read at least a few of them.

### ood-008 (ex05_iv_infusion, turn 1; tags: infusion, route-stated)

Request: Perfusion de 150 mg sur 2 h. Donne-moi le Cmax et l'AUC(0-t).

Why: refused / asked (ask) where the gold decisions expect an answer


Answer:

```text
Je ne lance pas l'analyse : la durée de la perfusion n'est pas indiquée. Précisez-la, dans l'unité de temps des données (h).
```

### ood-010 (ex12_iv_infusion, turn 1; tags: dose-unit-micro, duration-unit-mismatch, unit-in-text)

Request: Perfusion de 500 µg pendant 1,5 h, Cmax et AUC0-inf.

Why: refused / asked (ask) where the gold decisions expect an answer


Answer:

```text
Je ne lance pas l'analyse : la durée de la perfusion n'est pas indiquée. Précisez-la, dans l'unité de temps des données (min).
```

### ood-011 (ex12_iv_infusion, turn 1; tags: duration-word, colloquial, dose-unit-micro)

Request: Perfusion de 500 µg pendant 90 minutes : que vaut l'AUC(0-t) ?

Why: refused / asked (ask) where the gold decisions expect an answer


Answer:

```text
Je ne lance pas l'analyse : la durée de la perfusion n'est pas indiquée. Précisez-la, dans l'unité de temps des données (min).
```

### ood-013 (ex08_oral_1, turn 2; tags: compare, english-term, rerun)

Request: Compare l'AUC linéaire et la lin-up/log-down.

Why: refused / asked (which-pair) where the gold decisions expect an answer


Answer:

```text
Quelles analyses faut-il comparer ? Analyses du projet : analyse 2 (NCA, linéaire), analyse 3 (NCA, linear-up/log-down).
```

### ood-030 (ex03_pk2_iv_bolus, turn 2; tags: compare, rerun)

Request: Refais l'analyse en lin-up/log-down et compare les deux AUC en valeur et en %.

Why: refused / asked (which-pair) where the gold decisions expect an answer


Answer:

```text
Quelles analyses faut-il comparer ? Analyses du projet : analyse 2 (NCA, linéaire), analyse 3 (NCA, linear-up/log-down).
```

### ood-037 (ex05_iv_infusion, turn 1; tags: infusion, route-stated)

Request: Perfusion de 150 mg sur 2 h : clairance et volume de distribution.

Why: refused / asked (ask) where the gold decisions expect an answer


Answer:

```text
Je ne lance pas l'analyse : la durée de la perfusion n'est pas indiquée. Précisez-la, dans l'unité de temps des données (h).
```

### ood-043 (ex20_iv_infusion, turn 1; tags: infusion, abbreviation)

Request: Perfusion IV de 150 mg sur 2 h, CL et Vz svp.

Why: refused / asked (ask) where the gold decisions expect an answer


Answer:

```text
Je ne lance pas l'analyse : la durée de la perfusion n'est pas indiquée. Précisez-la, dans l'unité de temps des données (h).
```

### ood-055 (ex12_iv_infusion, turn 1; tags: infusion, dose-unit-micro)

Request: Perfusion de 500 µg sur 90 min : Cmax.

Why: refused / asked (ask) where the gold decisions expect an answer


Answer:

```text
Je ne lance pas l'analyse : la durée de la perfusion n'est pas indiquée. Précisez-la, dans l'unité de temps des données (min).
```

### ood-058 (ex02_oral_1, turn 1; tags: compare, no-prior-analysis)

Request: Compare les AUC linéaire et lin-up/log-down, dose orale de 400 mg.

Why: refused / asked (no-analysis) where the gold decisions expect an answer


Answer:

```text
Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, la voie et la méthode d'AUC).
```

### ood-062 (oodx04_infusion_dur_h, turn 1; tags: invented, duration-unit-mismatch, infusion)

Request: Perfusion de 75 mg sur 1,5 h, les temps sont en minutes : Cmax.

Why: refused / asked (ask) where the gold decisions expect an answer


Answer:

```text
Je ne lance pas l'analyse : la durée de la perfusion n'est pas indiquée. Précisez-la, dans l'unité de temps des données (min).
```

### ood-070 (oodx12_iv_infusion_mcg, turn 1; tags: invented, dose-unit-micro, infusion)

Request: Perfusion de 750 µg sur 1 h : Vz et CL.

Why: refused / asked (ask) where the gold decisions expect an answer


Answer:

```text
Je ne lance pas l'analyse : la durée de la perfusion n'est pas indiquée. Précisez-la, dans l'unité de temps des données (h).
```

### ood-071 (oodx01_oral_mg_ugml, turn 2; tags: invented, compare, rerun)

Request: Compare l'AUC linéaire et la lin-up/log-down.

Why: refused / asked (which-pair) where the gold decisions expect an answer


Answer:

```text
Quelles analyses faut-il comparer ? Analyses du projet : analyse 2 (NCA, linéaire), analyse 3 (NCA, linear-up/log-down).
```

