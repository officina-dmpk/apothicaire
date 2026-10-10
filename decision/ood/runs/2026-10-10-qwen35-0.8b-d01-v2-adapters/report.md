# Out-of-distribution requests: decider `qwen35-0.8b-d01-v2-adapters`, 2026-10-10

`decision/eval_ood.py`; 74 requests converted from `decision/ood/requests.jsonl` (schema report: `decision/ood/schema_report.md`).

## Scoring on the rows

74 rows, 1480 decisions: **93.9 %** correct overall; 22 of 74 rows have all their decisions right (29.7 %). Always-majority on these rows: 86.6 %; majority learned on train.jsonl: 81.4 %.

### Accuracy per question

| question | correct | total | accuracy | always-majority (these rows) | majority (train.jsonl) | ECE |
|---|---|---|---|---|---|---|
| analysis | 55 | 74 | 74.3 % | 60.8 % | 21.6 % | 0.229 |
| asked_adj_r2 | 74 | 74 | 100.0 % | 98.6 % | 98.6 % | 0.000 |
| asked_aucinf | 67 | 74 | 90.5 % | 91.9 % | 91.9 % | 0.088 |
| asked_auclast | 67 | 74 | 90.5 % | 73.0 % | 73.0 % | 0.092 |
| asked_aucpext | 72 | 74 | 97.3 % | 95.9 % | 95.9 % | 0.027 |
| asked_c0 | 74 | 74 | 100.0 % | 95.9 % | 95.9 % | 0.000 |
| asked_cl | 73 | 74 | 98.6 % | 87.8 % | 87.8 % | 0.014 |
| asked_cmax | 73 | 74 | 98.6 % | 70.3 % | 70.3 % | 0.014 |
| asked_half_life | 74 | 74 | 100.0 % | 87.8 % | 87.8 % | 0.000 |
| asked_lambda_z | 74 | 74 | 100.0 % | 98.6 % | 98.6 % | 0.000 |
| asked_lambda_z_points | 74 | 74 | 100.0 % | 97.3 % | 97.3 % | 0.000 |
| asked_mrt | 74 | 74 | 100.0 % | 95.9 % | 95.9 % | 0.000 |
| asked_tlag | 74 | 74 | 100.0 % | 94.6 % | 94.6 % | 0.000 |
| asked_tmax | 74 | 74 | 100.0 % | 90.5 % | 90.5 % | 0.000 |
| asked_vz | 73 | 74 | 98.6 % | 87.8 % | 87.8 % | 0.014 |
| auc_method | 50 | 74 | 67.6 % | 77.0 % | 12.2 % | 0.307 |
| compare_pair | 72 | 74 | 97.3 % | 94.6 % | 94.6 % | 0.025 |
| dose_has_unit | 72 | 74 | 97.3 % | 93.2 % | 93.2 % | 0.027 |
| is_not_available | 63 | 74 | 85.1 % | 85.1 % | 85.1 % | 0.148 |
| route | 60 | 74 | 81.1 % | 54.1 % | 54.1 % | 0.181 |
| **overall** | 1389 | 1480 | **93.9 %** | 86.6 % | 81.4 % | 0.057 |

### Confusions (wrong cells only: gold -> predicted, count)

- `analysis`: nca -> none_needed (14); none_needed -> not_supported (4); none_needed -> nca (1).
- `route`: oral -> unknown (6); iv_infusion -> unknown (5); iv_bolus -> unknown (2); iv_bolus -> iv_infusion (1).
- `auc_method`: linear -> not_applicable (21); lin_up_log_down -> not_applicable (2); not_applicable -> linear (1).
- `compare_pair`: 3+2 -> 2+3 (2).
- `is_not_available`: true -> false (11).
- `dose_has_unit`: false -> true (2).
- `asked_<parameter>` (14 questions): 3 parameters asked and missed (of 99 asked), 16 parameters predicted asked that were not.

### Accuracy per tag (which kinds of hard requests break)

| tag | rows | decisions correct | accuracy | rows all right |
|---|---|---|---|---|
| bioequivalence | 1 | 17/20 | 85.0 % | 0.0 % |
| by-id | 2 | 35/40 | 87.5 % | 0.0 % |
| compare | 8 | 147/160 | 91.9 % | 0.0 % |
| dose-unit-g | 1 | 18/20 | 90.0 % | 0.0 % |
| dose-unit-mcg | 1 | 18/20 | 90.0 % | 0.0 % |
| dose-unit-micro | 9 | 163/180 | 90.6 % | 0.0 % |
| dose-without-unit | 1 | 18/20 | 90.0 % | 0.0 % |
| duration-unit-mismatch | 2 | 36/40 | 90.0 % | 0.0 % |
| duration-word | 1 | 18/20 | 90.0 % | 0.0 % |
| english-term | 1 | 19/20 | 95.0 % | 0.0 % |
| follow-up | 4 | 76/80 | 95.0 % | 0.0 % |
| iv-explicit | 1 | 18/20 | 90.0 % | 0.0 % |
| multi-subject | 1 | 19/20 | 95.0 % | 0.0 % |
| multiple-dose | 1 | 15/20 | 75.0 % | 0.0 % |
| no-dose | 1 | 18/20 | 90.0 % | 0.0 % |
| no-parameter | 1 | 18/20 | 90.0 % | 0.0 % |
| no-prior-analysis | 1 | 19/20 | 95.0 % | 0.0 % |
| non-auc-parameter | 1 | 19/20 | 95.0 % | 0.0 % |
| out-of-scope | 4 | 66/80 | 82.5 % | 0.0 % |
| parameter-not-for-route | 5 | 89/100 | 89.0 % | 0.0 % |
| parameter-not-in-schema | 2 | 36/40 | 90.0 % | 0.0 % |
| plain | 2 | 38/40 | 95.0 % | 0.0 % |
| population | 1 | 17/20 | 85.0 % | 0.0 % |
| recall | 1 | 19/20 | 95.0 % | 0.0 % |
| rerun | 4 | 75/80 | 93.8 % | 0.0 % |
| route-missing | 1 | 18/20 | 90.0 % | 0.0 % |
| steady-state | 1 | 15/20 | 75.0 % | 0.0 % |
| terminology-mismatch | 2 | 37/40 | 92.5 % | 0.0 % |
| tlag | 1 | 18/20 | 90.0 % | 0.0 % |
| unicode | 1 | 19/20 | 95.0 % | 0.0 % |
| unit-variety | 1 | 19/20 | 95.0 % | 0.0 % |
| unrecognized-unit | 1 | 18/20 | 90.0 % | 0.0 % |
| urine | 1 | 17/20 | 85.0 % | 0.0 % |
| invented | 16 | 292/320 | 91.2 % | 12.5 % |
| infusion | 7 | 131/140 | 93.6 % | 28.6 % |
| latin-route | 3 | 58/60 | 96.7 % | 33.3 % |
| route-implied | 5 | 95/100 | 95.0 % | 40.0 % |
| abbreviation | 17 | 327/340 | 96.2 % | 41.2 % |
| blq | 4 | 78/80 | 97.5 % | 50.0 % |
| colloquial | 6 | 114/120 | 95.0 % | 50.0 % |
| language-mix | 2 | 39/40 | 97.5 % | 50.0 % |
| method-explicit | 2 | 39/40 | 97.5 % | 50.0 % |
| two-requests-in-one-sentence | 2 | 39/40 | 97.5 % | 50.0 % |
| typo | 2 | 39/40 | 97.5 % | 50.0 % |
| unit-in-text | 5 | 96/100 | 96.0 % | 60.0 % |
| route-stated | 8 | 155/160 | 96.9 % | 62.5 % |
| fit | 4 | 79/80 | 98.8 % | 75.0 % |
| c0 | 1 | 20/20 | 100.0 % | 100.0 % |
| dose-unit-mg | 1 | 20/20 | 100.0 % | 100.0 % |
| oral | 1 | 20/20 | 100.0 % | 100.0 % |
| simulate | 1 | 20/20 | 100.0 % | 100.0 % |
| two-compartments | 2 | 40/40 | 100.0 % | 100.0 % |
| unit-conversion-in-text | 1 | 20/20 | 100.0 % | 100.0 % |

Tags that broke (share of fully correct rows below the overall share): bioequivalence, by-id, compare, dose-unit-g, dose-unit-mcg, dose-unit-micro, dose-without-unit, duration-unit-mismatch, duration-word, english-term, follow-up, infusion, invented, iv-explicit, multi-subject, multiple-dose, no-dose, no-parameter, no-prior-analysis, non-auc-parameter, out-of-scope, parameter-not-for-route, parameter-not-in-schema, plain, population, recall, rerun, route-missing, steady-state, terminology-mismatch, tlag, unicode, unit-variety, unrecognized-unit, urine.

### Calibration (probability of the chosen label vs observed accuracy)

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 0 | - | - |
| [0.3, 0.4) | 0 | - | - |
| [0.4, 0.5) | 0 | - | - |
| [0.5, 0.6) | 7 | 0.557 | 0.429 |
| [0.6, 0.7) | 2 | 0.675 | 0.000 |
| [0.7, 0.8) | 5 | 0.731 | 0.000 |
| [0.8, 0.9) | 5 | 0.862 | 0.400 |
| [0.9, 1.0] | 1461 | 0.999 | 0.947 |

Expected calibration error: 0.057.

### Wrong decisions (91)

| row | question | gold | predicted | confidence | request |
|---|---|---|---|---|---|
| ood-002 | auc_method | linear | not_applicable | 1.00 | et la t1/2 stp ? |
| ood-003 | auc_method | linear | not_applicable | 1.00 | AUC0-t et AUC0-inf svp |
| ood-005 | analysis | nca | none_needed | 0.94 | bolus de 200 mg : Cl/F ? |
| ood-005 | auc_method | linear | not_applicable | 1.00 | bolus de 200 mg : Cl/F ? |
| ood-007 | route | iv_bolus | unknown | 0.52 | fit un modèle mono-compartiment sur ces données (bolus de 300 mg) |
| ood-009 | auc_method | linear | not_applicable | 1.00 | Et la MRT ? |
| ood-010 | asked_auclast | false | true | 1.00 | Perfusion de 500 µg pendant 1,5 h, Cmax et AUC0-inf. |
| ood-010 | route | iv_infusion | unknown | 1.00 | Perfusion de 500 µg pendant 1,5 h, Cmax et AUC0-inf. |
| ood-011 | analysis | nca | none_needed | 0.96 | Perfusion de 500 µg pendant 90 minutes : que vaut l'AUC(0-t) ? |
| ood-011 | route | iv_infusion | unknown | 1.00 | Perfusion de 500 µg pendant 90 minutes : que vaut l'AUC(0-t) ? |
| ood-012 | asked_aucinf | false | true | 1.00 | J'ai avalé 800 µg, les temps sont en minutes ; Cmax et AUC0-t. |
| ood-012 | route | oral | unknown | 1.00 | J'ai avalé 800 µg, les temps sont en minutes ; Cmax et AUC0-t. |
| ood-013 | asked_auclast | true | false | 1.00 | Compare l'AUC linéaire et la lin-up/log-down. |
| ood-014 | asked_aucpext | false | true | 1.00 | Compare les deux AUC (valeur et %). |
| ood-014 | auc_method | linear | not_applicable | 1.00 | Compare les deux AUC (valeur et %). |
| ood-015 | auc_method | lin_up_log_down | not_applicable | 1.00 | Compare l'analyse 2 à l'analyse 1. |
| ood-015 | compare_pair | 3+2 | 2+3 | 1.00 | Compare l'analyse 2 à l'analyse 1. |
| ood-016 | analysis | nca | none_needed | 0.98 | Voie orale, 300 mg : y a-t-il un Tlag ? |
| ood-016 | auc_method | linear | not_applicable | 1.00 | Voie orale, 300 mg : y a-t-il un Tlag ? |
| ood-017 | auc_method | linear | not_applicable | 1.00 | Quel est le Tlag de ce bolus de 200 mg ? |
| ood-017 | is_not_available | true | false | 0.99 | Quel est le Tlag de ce bolus de 200 mg ? |
| ood-018 | auc_method | linear | not_applicable | 1.00 | Quelle est la C0 après cette prise orale de 400 mg ? |
| ood-018 | is_not_available | true | false | 0.99 | Quelle est la C0 après cette prise orale de 400 mg ? |
| ood-019 | analysis | none_needed | not_supported | 1.00 | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-019 | is_not_available | true | false | 1.00 | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-019 | route | oral | unknown | 1.00 | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-020 | analysis | none_needed | not_supported | 1.00 | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. |
| ood-020 | is_not_available | true | false | 1.00 | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. |
| ood-020 | route | oral | unknown | 1.00 | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. |
| ood-021 | analysis | nca | none_needed | 0.87 | Après une prise orale, voici mes concentrations : quelle est la demi-vie ? |
| ood-021 | auc_method | linear | not_applicable | 1.00 | Après une prise orale, voici mes concentrations : quelle est la demi-vie ? |
| ood-022 | analysis | nca | none_needed | 0.98 | Prise orale de 100, voici les données. Cmax ? |
| ood-022 | auc_method | linear | not_applicable | 0.91 | Prise orale de 100, voici les données. Cmax ? |
| ood-024 | analysis | nca | none_needed | 0.73 | Bolus de 2000 mcg : CL et Vz. |
| ood-024 | dose_has_unit | false | true | 1.00 | Bolus de 2000 mcg : CL et Vz. |
| ood-025 | auc_method | linear | not_applicable | 1.00 | Et le pourcentage d'AUC extrapolée ? |
| ood-029 | route | iv_bolus | unknown | 0.91 | Donne-moi le Cmax puis refais l'analyse en lin-up/log-down, bolus de 300 mg. |
| ood-030 | asked_aucinf | false | true | 0.98 | Refais l'analyse en lin-up/log-down et compare les deux AUC en valeur et en %. |
| ood-030 | asked_aucpext | false | true | 1.00 | Refais l'analyse en lin-up/log-down et compare les deux AUC en valeur et en %. |
| ood-034 | asked_vz | false | true | 1.00 | Bolus de 150 mg : quel est le Vdss ? |
| ood-034 | is_not_available | true | false | 1.00 | Bolus de 150 mg : quel est le Vdss ? |
| ood-037 | route | iv_infusion | unknown | 1.00 | Perfusion de 150 mg sur 2 h : clairance et volume de distribution. |
| ood-038 | auc_method | linear | not_applicable | 1.00 | Quel est le Tlag de cette perfusion de 150 mg ? |
| ood-038 | is_not_available | true | false | 0.99 | Quel est le Tlag de cette perfusion de 150 mg ? |
| ood-039 | asked_auclast | false | true | 1.00 | Dose IV de 1000 µg : AUC(0-inf) et pourcentage extrapolé. |
| ood-039 | route | iv_bolus | iv_infusion | 1.00 | Dose IV de 1000 µg : AUC(0-inf) et pourcentage extrapolé. |
| ood-040 | analysis | nca | none_needed | 0.60 | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? |
| ood-040 | auc_method | linear | not_applicable | 1.00 | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? |
| ood-040 | route | oral | unknown | 1.00 | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? |
| ood-044 | route | oral | unknown | 1.00 | Comprimé à libération prolongée de 5000 µg : Cmax, Tmax et demi-vie. |
| ood-046 | analysis | nca | none_needed | 1.00 | Bolus de 150 mg : le Cl/F et le Vz/F ? |
| ood-047 | auc_method | linear | not_applicable | 0.96 | Voie orale, 100 mg : λz et t½. |
| ood-048 | auc_method | linear | not_applicable | 1.00 | Voie orale, 300 mg : quelle est la constante d'absorption ka ? |
| ood-048 | is_not_available | true | false | 0.99 | Voie orale, 300 mg : quelle est la constante d'absorption ka ? |
| ood-051 | analysis | nca | none_needed | 0.71 | Bolus de 2000 µg : l'AUC(0-t) tient-elle compte du point sous la LLOQ ? et le % extrapolé ? |
| ood-052 | asked_aucinf | false | true | 1.00 | Dose orale de 500 mg, méthode des trapèzes linéaires : AUC0-t. |
| ood-053 | analysis | nca | none_needed | 1.00 | Voici mes concentrations après 400 mg ; quel est le Cmax ? |
| ood-053 | auc_method | linear | not_applicable | 0.70 | Voici mes concentrations après 400 mg ; quel est le Cmax ? |
| ood-055 | analysis | nca | none_needed | 0.98 | Perfusion de 500 µg sur 90 min : Cmax. |
| ood-055 | route | iv_infusion | unknown | 1.00 | Perfusion de 500 µg sur 90 min : Cmax. |
| ood-056 | auc_method | linear | not_applicable | 1.00 | Rappelle-moi la dose et la méthode d'AUC utilisées. |
| ood-057 | auc_method | linear | not_applicable | 1.00 | Compare le Cmax entre les deux méthodes. |
| ood-058 | asked_aucinf | false | true | 0.52 | Compare les AUC linéaire et lin-up/log-down, dose orale de 400 mg. |
| ood-059 | asked_auclast | false | true | 1.00 | 250 mg per os, voici les concentrations en µg/mL : Cmax, Tmax et AUC0-inf. |
| ood-060 | auc_method | linear | not_applicable | 0.75 | Bolus IV de 120 mg : quel est le Tlag ? |
| ood-060 | is_not_available | true | false | 0.99 | Bolus IV de 120 mg : quel est le Tlag ? |
| ood-061 | analysis | none_needed | nca | 0.98 | Quelle est la C0 après cette prise orale de 200 mg ? |
| ood-061 | auc_method | linear | not_applicable | 1.00 | Quelle est la C0 après cette prise orale de 200 mg ? |
| ood-061 | is_not_available | true | false | 0.99 | Quelle est la C0 après cette prise orale de 200 mg ? |
| ood-062 | analysis | nca | none_needed | 0.66 | Perfusion de 75 mg sur 1,5 h, les temps sont en minutes : Cmax. |
| ood-062 | auc_method | linear | not_applicable | 0.76 | Perfusion de 75 mg sur 1,5 h, les temps sont en minutes : Cmax. |
| ood-063 | asked_aucinf | false | true | 1.00 | Étude à deux sujets, 300 mg par voie orale : Cmax et AUC0-t par sujet. |
| ood-064 | analysis | none_needed | not_supported | 1.00 | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-064 | asked_cmax | false | true | 1.00 | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-064 | auc_method | not_applicable | linear | 0.59 | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-064 | is_not_available | true | false | 1.00 | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-064 | route | oral | unknown | 1.00 | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-065 | analysis | none_needed | not_supported | 1.00 | Recueil urinaire : quantité excrétée et clairance rénale. |
| ood-065 | asked_cl | false | true | 1.00 | Recueil urinaire : quantité excrétée et clairance rénale. |
| ood-065 | is_not_available | true | false | 1.00 | Recueil urinaire : quantité excrétée et clairance rénale. |
| ood-068 | analysis | nca | none_needed | 0.69 | 80 mg per os, il y a des zéros sous la LLOQ : AUC(0-t) et Cmax. |
| ood-069 | asked_aucinf | false | true | 1.00 | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. |
| ood-069 | dose_has_unit | false | true | 1.00 | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. |
| ood-070 | analysis | nca | none_needed | 0.91 | Perfusion de 750 µg sur 1 h : Vz et CL. |
| ood-070 | route | iv_infusion | unknown | 1.00 | Perfusion de 750 µg sur 1 h : Vz et CL. |
| ood-071 | asked_auclast | true | false | 0.83 | Compare l'AUC linéaire et la lin-up/log-down. |
| ood-072 | asked_auclast | true | false | 1.00 | Compare l'analyse 2 et l'analyse 1 pour l'AUC. |
| ood-072 | auc_method | lin_up_log_down | not_applicable | 1.00 | Compare l'analyse 2 et l'analyse 1 pour l'AUC. |
| ood-072 | compare_pair | 3+2 | 2+3 | 0.86 | Compare l'analyse 2 et l'analyse 1 pour l'AUC. |
| ood-073 | asked_aucinf | false | true | 1.00 | Prise orale de 200 mg : Cmax, Tmax et AUC0-t. |
| ood-074 | asked_auclast | false | true | 1.00 | Bolus de 120 mg : Cmax et AUC0-inf. |

## Harness run

74 requests, one fresh Caladrius session each: **38 answers with values, 36 refusals or questions back**, 0 errors, 0 skipped (prior analyses that cannot be replayed).

| kind of answer | count |
|---|---|
| answer | 38 |
| refusal:ask | 6 |
| refusal:no-analysis | 20 |
| refusal:not-available | 1 |
| refusal:not-supported | 4 |
| refusal:not-wired | 5 |

No oracle applies to free requests (bench/score.py reads the scripted turns). Instead:

- answered where the gold decisions expect a refusal or a question back (the dangerous direction): 2 (ood-061, ood-069)
- refused or asked where the gold decisions expect an answer: 17 (ood-005, ood-008, ood-010, ood-011, ood-012, ood-016, ood-037, ood-039, ood-040, ood-044, ood-046, ood-051, ood-055, ood-058, ood-062, ood-068, ood-070)
- rows whose state, rebuilt by the harness, differs from the scored row: 0
- decisions that came back outside the offered options: 0

## What a human must read (64 of 74 requests)

Wrong decisions in the run, answers that contradict the gold decisions, errors, and the requests of the tags that broke (at most 6 per tag). Every other answer is in `answers.jsonl`; a correct decision does not make a correct answer, so read at least a few of them.

### ood-001 (ex02_oral_1, turn 1; tags: colloquial, route-implied)

Request: J'ai pris un comprimé de 400 mg ce matin, voici mes concentrations. C'est quoi le Cmax et le Tmax ?

Why: wrong decision: auc_method

- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC linear-up/log-down, dose 400 mg, voie orale (extravasculaire)) :
- Cmax : 8150 ng/mL
- Tmax : 2.8 h
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-002 (ex02_oral_1, turn 2; tags: abbreviation, typo, follow-up)

Request: et la t1/2 stp ?

Why: wrong decision: auc_method; tag that broke: follow-up

- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC trapèzes linéaires (linear), dose 400 mg, voie orale (extravasculaire)) :
- t½ (demi-vie terminale) : 3.9095 h
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-003 (ex02_oral_1, turn 2; tags: abbreviation, follow-up)

Request: AUC0-t et AUC0-inf svp

Why: wrong decision: auc_method; tag that broke: follow-up

- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC trapèzes linéaires (linear), dose 400 mg, voie orale (extravasculaire)) :
- AUC(0-tlast) : 76985 h*ng/mL
- AUC(0-inf) : 79657.9 h*ng/mL
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-004 (ex01_iv_bolus, turn 1; tags: abbreviation, route-stated)

Request: bolus IV de 200 mg ; quel est le Vd ?

Why: wrong decision: auc_method

- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC linear-up/log-down, dose 200 mg, bolus intraveineux) :
- Vz (volume de distribution) : 42.4968 dose unit/(mg/L)
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-005 (ex01_iv_bolus, turn 1; tags: abbreviation, terminology-mismatch)

Request: bolus de 200 mg : Cl/F ?

Why: wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: terminology-mismatch

- `analysis`: gold nca, predicted none_needed
- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, la voie et la méthode d'AUC).
```

### ood-008 (ex05_iv_infusion, turn 1; tags: infusion, route-stated)

Request: Perfusion de 150 mg sur 2 h. Donne-moi le Cmax et l'AUC(0-t).

Why: wrong decision: route; refused / asked (ask) where the gold decisions expect an answer; tag that broke: infusion

- `route`: gold iv_infusion, predicted unknown

Answer:

```text
Je ne lance pas l'analyse : la voie d'administration n'est pas indiquée. Précisez-la (bolus intraveineux, perfusion intraveineuse avec sa durée, ou voie orale).
```

### ood-009 (ex05_iv_infusion, turn 2; tags: abbreviation, follow-up)

Request: Et la MRT ?

Why: wrong decision: auc_method; tag that broke: follow-up

- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC trapèzes linéaires (linear), dose 150 mg, perfusion intraveineuse de 2 h) :
- MRT (temps moyen de résidence) : 5.22856 h
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-010 (ex12_iv_infusion, turn 1; tags: dose-unit-micro, duration-unit-mismatch, unit-in-text)

Request: Perfusion de 500 µg pendant 1,5 h, Cmax et AUC0-inf.

Why: wrong decision: asked_auclast, route; refused / asked (ask) where the gold decisions expect an answer; tag that broke: dose-unit-micro; tag that broke: duration-unit-mismatch

- `asked_auclast`: gold false, predicted true
- `route`: gold iv_infusion, predicted unknown

Answer:

```text
Je ne lance pas l'analyse : la voie d'administration n'est pas indiquée. Précisez-la (bolus intraveineux, perfusion intraveineuse avec sa durée, ou voie orale).
```

### ood-011 (ex12_iv_infusion, turn 1; tags: duration-word, colloquial, dose-unit-micro)

Request: Perfusion de 500 µg pendant 90 minutes : que vaut l'AUC(0-t) ?

Why: wrong decision: analysis, auc_method, route; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: duration-word; tag that broke: dose-unit-micro

- `analysis`: gold nca, predicted none_needed
- `auc_method`: gold linear, predicted not_applicable
- `route`: gold iv_infusion, predicted unknown

Answer:

```text
Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, la voie et la méthode d'AUC).
```

### ood-012 (ex08_oral_1, turn 1; tags: abbreviation, route-implied, dose-unit-micro)

Request: J'ai avalé 800 µg, les temps sont en minutes ; Cmax et AUC0-t.

Why: wrong decision: route; refused / asked (ask) where the gold decisions expect an answer; tag that broke: dose-unit-micro

- `route`: gold oral, predicted unknown

Answer:

```text
Je ne lance pas l'analyse : la voie d'administration n'est pas indiquée. Précisez-la (bolus intraveineux, perfusion intraveineuse avec sa durée, ou voie orale).
```

### ood-013 (ex08_oral_1, turn 2; tags: compare, english-term, rerun)

Request: Compare l'AUC linéaire et la lin-up/log-down.

Why: wrong decision: asked_auclast; tag that broke: compare; tag that broke: english-term; tag that broke: rerun

- `asked_auclast`: gold true, predicted false

Answer:

```text
Comparaison calculée par Caladrius entre l'analyse 2 et l'analyse 3 (b - a ; a = analyse 2, la référence ; b = analyse 3, comparée à la référence) :
- Cmax : analyse 2 39.91 ng/mL ; analyse 3 39.91 ng/mL ; différence 0 ng/mL ; différence relative 0 % ; rapport b/a 1
- Tmax : analyse 2 220 min ; analyse 3 220 min ; différence 0 min ; différence relative 0 % ; rapport b/a 1
- tfirst : analyse 2 16 min ; analyse 3 16 min ; différence 0 min ; différence relative 0 % ; rapport b/a 1
- Tlag (temps de latence) : analyse 2 0 min ; analyse 3 0 min ; différence 0 min
- tlast : analyse 2 3100 min ; analyse 3 3100 min ; différence 0 min ; différence relative 0 % ; rapport b/a 1
- clast.obs : analyse 2 1.765 ng/mL ; analyse 3 1.765 ng/mL ; différence 0 ng/mL ; différence relative 0 % ; rapport b/a 1
- AUC(0-tlast) : analyse 2 46762.6 min*ng/mL ; analyse 3 42680.3 min*ng/mL ; différence -4082.31 min*ng/mL ; différence relative -8.72987 % ; rapport b/a 0.912701
- aucall : analyse 2 46762.6 min*ng/mL ; analyse 3 42680.3 min*ng/mL ; différence -4082.31 min*ng/mL ; différence relative -8.72987 % ; rapport b/a 0.912701
- aumclast : analyse 2 37143000 min^2*ng/mL ; analyse 3 37473700 min^2*ng/mL ; différence 330636 min^2*ng/mL ; différence relative 0.89017 % ; rapport b/a 1.0089
- aumcall : analyse 2 37143000 min^2*ng/mL ; analyse 3 37473700 min^2*ng/mL ; différence 330636 min^2*ng/mL ; différence relative 0.89017 % ; rapport b/a 1.0089
- λz (constante d'élimination terminale) : analyse 2 0.0011 [...]
```

### ood-014 (ex08_oral_1, turn 2; tags: compare)

Request: Compare les deux AUC (valeur et %).

Why: wrong decision: asked_auclast, asked_aucpext, auc_method; tag that broke: compare

- `asked_auclast`: gold true, predicted false
- `asked_aucpext`: gold false, predicted true
- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Comparaison calculée par Caladrius entre l'analyse 2 et l'analyse 3 (b - a ; a = analyse 2, la référence ; b = analyse 3, comparée à la référence) :
- AUC extrapolée (%), méthode linéaire (analyse 2) : 3.31685 %
- AUC extrapolée (%), méthode linear-up/log-down (analyse 3) : 3.62261 %
- Différence (b - a) : 0.305759 %
- Différence relative : 9.21837 %
- Rapport b/a : 1.09218
```

### ood-015 (ex08_oral_1, turn 2; tags: compare, by-id, no-parameter)

Request: Compare l'analyse 2 à l'analyse 1.

Why: wrong decision: auc_method, compare_pair; tag that broke: compare; tag that broke: by-id; tag that broke: no-parameter

- `auc_method`: gold lin_up_log_down, predicted not_applicable
- `compare_pair`: gold 3+2, predicted 2+3

Answer:

```text
Comparaison calculée par Caladrius entre l'analyse 2 et l'analyse 3 (b - a ; a = analyse 2, la référence ; b = analyse 3, comparée à la référence) :
- Cmax : analyse 2 39.91 ng/mL ; analyse 3 39.91 ng/mL ; différence 0 ng/mL ; différence relative 0 % ; rapport b/a 1
- Tmax : analyse 2 220 min ; analyse 3 220 min ; différence 0 min ; différence relative 0 % ; rapport b/a 1
- tfirst : analyse 2 16 min ; analyse 3 16 min ; différence 0 min ; différence relative 0 % ; rapport b/a 1
- Tlag (temps de latence) : analyse 2 0 min ; analyse 3 0 min ; différence 0 min
- tlast : analyse 2 3100 min ; analyse 3 3100 min ; différence 0 min ; différence relative 0 % ; rapport b/a 1
- clast.obs : analyse 2 1.765 ng/mL ; analyse 3 1.765 ng/mL ; différence 0 ng/mL ; différence relative 0 % ; rapport b/a 1
- AUC(0-tlast) : analyse 2 46762.6 min*ng/mL ; analyse 3 42680.3 min*ng/mL ; différence -4082.31 min*ng/mL ; différence relative -8.72987 % ; rapport b/a 0.912701
- aucall : analyse 2 46762.6 min*ng/mL ; analyse 3 42680.3 min*ng/mL ; différence -4082.31 min*ng/mL ; différence relative -8.72987 % ; rapport b/a 0.912701
- aumclast : analyse 2 37143000 min^2*ng/mL ; analyse 3 37473700 min^2*ng/mL ; différence 330636 min^2*ng/mL ; différence relative 0.89017 % ; rapport b/a 1.0089
- aumcall : analyse 2 37143000 min^2*ng/mL ; analyse 3 37473700 min^2*ng/mL ; différence 330636 min^2*ng/mL ; différence relative 0.89017 % ; rapport b/a 1.0089
- λz (constante d'élimination terminale) : analyse 2 0.0011 [...]
```

### ood-016 (ex04_oral_1_lag, turn 1; tags: route-stated, tlag)

Request: Voie orale, 300 mg : y a-t-il un Tlag ?

Why: wrong decision: analysis, asked_tmax, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: tlag

- `analysis`: gold nca, predicted none_needed
- `asked_tmax`: gold false, predicted true
- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, la voie et la méthode d'AUC).
```

### ood-017 (ex01_iv_bolus, turn 1; tags: parameter-not-for-route, iv-explicit)

Request: Quel est le Tlag de ce bolus de 200 mg ?

Why: wrong decision: auc_method, is_not_available; tag that broke: parameter-not-for-route; tag that broke: iv-explicit

- `auc_method`: gold linear, predicted not_applicable
- `is_not_available`: gold true, predicted false

Answer:

```text
Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, la voie et la méthode d'AUC).
```

### ood-018 (ex02_oral_1, turn 1; tags: parameter-not-for-route)

Request: Quelle est la C0 après cette prise orale de 400 mg ?

Why: wrong decision: auc_method; tag that broke: parameter-not-for-route

- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
C0 (concentration initiale extrapolée) n'est pas calculé par Caladrius pour cette voie d'administration ; aucune analyse n'est encore faite.
```

### ood-019 (ex02_oral_1, turn 1; tags: out-of-scope, bioequivalence)

Request: Ce produit de 400 mg est-il bioéquivalent au princeps ?

Why: wrong decision: analysis, is_not_available, route; tag that broke: out-of-scope; tag that broke: bioequivalence

- `analysis`: gold none_needed, predicted not_supported
- `is_not_available`: gold true, predicted false
- `route`: gold oral, predicted unknown

Answer:

```text
Cette demande (hors du périmètre du harnais) n'est pas prise en charge : le harnais de décision sait lancer une analyse non compartimentale, en donner les paramètres usuels (Cmax, Tmax, C0, AUC, λz, t½, CL, Vz, MRT, Tlag...), rappeler ses réglages et comparer deux analyses ; il ne fait rien d'autre (ni bioéquivalence, ni modèle de population, ni état d'équilibre, ni excrétion urinaire, ni explication rédigée). Je ne donne aucune valeur.
```

### ood-020 (ex02_oral_1, turn 1; tags: out-of-scope, population)

Request: Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg.

Why: wrong decision: analysis, is_not_available, route; tag that broke: out-of-scope; tag that broke: population

- `analysis`: gold none_needed, predicted not_supported
- `is_not_available`: gold true, predicted false
- `route`: gold oral, predicted unknown

Answer:

```text
Cette demande (hors du périmètre du harnais) n'est pas prise en charge : le harnais de décision sait lancer une analyse non compartimentale, en donner les paramètres usuels (Cmax, Tmax, C0, AUC, λz, t½, CL, Vz, MRT, Tlag...), rappeler ses réglages et comparer deux analyses ; il ne fait rien d'autre (ni bioéquivalence, ni modèle de population, ni état d'équilibre, ni excrétion urinaire, ni explication rédigée). Je ne donne aucune valeur.
```

### ood-021 (ex06_oral_0, turn 1; tags: no-dose, route-implied)

Request: Après une prise orale, voici mes concentrations : quelle est la demi-vie ?

Why: wrong decision: analysis, auc_method; tag that broke: no-dose

- `analysis`: gold nca, predicted none_needed
- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, la voie et la méthode d'AUC).
```

### ood-022 (ex06_oral_0, turn 1; tags: dose-without-unit)

Request: Prise orale de 100, voici les données. Cmax ?

Why: wrong decision: analysis, auc_method; tag that broke: dose-without-unit

- `analysis`: gold nca, predicted none_needed
- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, la voie et la méthode d'AUC).
```

### ood-023 (ex07_iv_bolus, turn 1; tags: unit-conversion-in-text, dose-unit-mg)

Request: Bolus IV de 2 mg : donne-moi la clairance et le Vz.

Why: wrong decision: auc_method

- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC linear-up/log-down, dose 2 mg, bolus intraveineux) :
- CL (clairance) : 0.011158 dose unit/(h*ng/mL), soit 11.158 L/h (conversion faite par Caladrius avec la dose en mg)
- Vz (volume de distribution) : 0.0716391 dose unit/(ng/mL), soit 71.6391 L (conversion faite par Caladrius avec la dose en mg)
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-024 (ex07_iv_bolus, turn 1; tags: dose-unit-mcg, unrecognized-unit)

Request: Bolus de 2000 mcg : CL et Vz.

Why: wrong decision: analysis, auc_method, dose_has_unit; tag that broke: dose-unit-mcg; tag that broke: unrecognized-unit

- `analysis`: gold nca, predicted none_needed
- `auc_method`: gold linear, predicted not_applicable
- `dose_has_unit`: gold false, predicted true

Answer:

```text
Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, la voie et la méthode d'AUC).
```

### ood-025 (ex07_iv_bolus, turn 2; tags: follow-up, abbreviation)

Request: Et le pourcentage d'AUC extrapolée ?

Why: wrong decision: auc_method; tag that broke: follow-up

- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC trapèzes linéaires (linear), dose 2000 µg, bolus intraveineux) :
- AUC extrapolée (%) : 2.70114 %
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-028 (ex09_pk2_oral_1, turn 1; tags: two-requests-in-one-sentence)

Request: Donne-moi d'abord la demi-vie, ensuite la clairance et le Vz, pour cette dose orale de 300 mg.

Why: wrong decision: auc_method

- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC linear-up/log-down, dose 300 mg, voie orale (extravasculaire)) :
- t½ (demi-vie terminale) : 5.8965 h
- CL/F (clairance) : 0.00679702 dose unit/(h*ng/mL), soit 6.79702 L/h (conversion faite par Caladrius avec la dose en mg)
- Vz/F (volume de distribution) : 0.0578213 dose unit/(ng/mL), soit 57.8213 L (conversion faite par Caladrius avec la dose en mg)
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-029 (ex03_pk2_iv_bolus, turn 1; tags: two-requests-in-one-sentence, rerun)

Request: Donne-moi le Cmax puis refais l'analyse en lin-up/log-down, bolus de 300 mg.

Why: tag that broke: rerun


Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC linear-up/log-down, dose 300 mg, bolus intraveineux) :
- Cmax : 8.391 mg/L
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-030 (ex03_pk2_iv_bolus, turn 2; tags: compare, rerun)

Request: Refais l'analyse en lin-up/log-down et compare les deux AUC en valeur et en %.

Why: wrong decision: asked_aucpext; tag that broke: compare; tag that broke: rerun

- `asked_aucpext`: gold false, predicted true

Answer:

```text
Comparaison calculée par Caladrius entre l'analyse 2 et l'analyse 3 (b - a ; a = analyse 2, la référence ; b = analyse 3, comparée à la référence) :
- AUC(0-tlast) : analyse 2 128.516 h*mg/L ; analyse 3 125.47 h*mg/L ; différence -3.04581 h*mg/L ; différence relative -2.36999 % ; rapport b/a 0.9763
- AUC extrapolée (%) : analyse 2 2.86723 % ; analyse 3 2.93479 % ; différence 0.0675598 % ; différence relative 2.35628 % ; rapport b/a 1.02356
```

### ood-031 (ex10_oral_1_lag, turn 1; tags: language-mix, abbreviation)

Request: Peux-tu me donner le Cmax, le Tmax et le t1/2 after a single oral dose of 100 mg ?

Why: wrong decision: auc_method

- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC linear-up/log-down, dose 100 mg, voie orale (extravasculaire)) :
- Cmax : 2.295 mg/L
- Tmax : 2.4 h
- t½ (demi-vie terminale) : 4.80769 h
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-032 (ex02_oral_1, turn 1; tags: typo, colloquial, latin-route)

Request: kel est le Cmax é le Tmax de ce tablo ? dose 400 mg per os

Why: wrong decision: auc_method

- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC linear-up/log-down, dose 400 mg, voie orale (extravasculaire)) :
- Cmax : 8150 ng/mL
- Tmax : 2.8 h
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-034 (ex14_iv_bolus, turn 1; tags: parameter-not-in-schema, abbreviation)

Request: Bolus de 150 mg : quel est le Vdss ?

Why: wrong decision: asked_vz, auc_method, is_not_available; tag that broke: parameter-not-in-schema

- `asked_vz`: gold false, predicted true
- `auc_method`: gold linear, predicted not_applicable
- `is_not_available`: gold true, predicted false

Answer:

```text
Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, la voie et la méthode d'AUC).
```

### ood-035 (ex14_iv_bolus, turn 1; tags: abbreviation)

Request: Bolus de 150 mg : le R² ajusté et le nombre de points de la régression terminale.

Why: wrong decision: auc_method

- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC linear-up/log-down, dose 150 mg, bolus intraveineux) :
- R² ajusté de la régression terminale : 0.999573
- Nombre de points de la régression terminale : 3
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
Alerte qualité de Caladrius : « the terminal phase spans 1.98 half-lives (< 2); λz and the extrapolated values are uncertain, sample longer if possible ».
```

### ood-036 (ex25_oral_1, turn 1; tags: abbreviation)

Request: Prise unique de 100 mg par voie orale : je veux le MRT et la demi-vie.

Why: wrong decision: auc_method

- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC linear-up/log-down, dose 100 mg, voie orale (extravasculaire)) :
- t½ (demi-vie terminale) : 8.45998 h
- MRT (temps moyen de résidence) : 13.9765 h
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-037 (ex05_iv_infusion, turn 1; tags: infusion, route-stated)

Request: Perfusion de 150 mg sur 2 h : clairance et volume de distribution.

Why: wrong decision: auc_method, route; refused / asked (ask) where the gold decisions expect an answer; tag that broke: infusion

- `auc_method`: gold linear, predicted not_applicable
- `route`: gold iv_infusion, predicted unknown

Answer:

```text
Je ne lance pas l'analyse : la voie d'administration n'est pas indiquée. Précisez-la (bolus intraveineux, perfusion intraveineuse avec sa durée, ou voie orale).
```

### ood-038 (ex05_iv_infusion, turn 1; tags: parameter-not-for-route, infusion)

Request: Quel est le Tlag de cette perfusion de 150 mg ?

Why: wrong decision: auc_method, is_not_available; tag that broke: parameter-not-for-route; tag that broke: infusion

- `auc_method`: gold linear, predicted not_applicable
- `is_not_available`: gold true, predicted false

Answer:

```text
Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, la voie et la méthode d'AUC).
```

### ood-039 (ex11_pk2_iv_bolus, turn 1; tags: dose-unit-micro, route-stated)

Request: Dose IV de 1000 µg : AUC(0-inf) et pourcentage extrapolé.

Why: wrong decision: asked_auclast, route; refused / asked (ask) where the gold decisions expect an answer; tag that broke: dose-unit-micro

- `asked_auclast`: gold false, predicted true
- `route`: gold iv_bolus, predicted iv_infusion

Answer:

```text
Je ne lance pas l'analyse : la durée de la perfusion n'est pas indiquée. Précisez-la, dans l'unité de temps des données (h).
```

### ood-040 (ex16_pk2_oral_1, turn 1; tags: colloquial, dose-unit-micro)

Request: J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ?

Why: wrong decision: analysis, auc_method, route; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: dose-unit-micro

- `analysis`: gold nca, predicted none_needed
- `auc_method`: gold linear, predicted not_applicable
- `route`: gold oral, predicted unknown

Answer:

```text
Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, la voie et la méthode d'AUC).
```

### ood-041 (ex18_pk2_iv_bolus, turn 1; tags: route-stated, unit-in-text)

Request: Bolus de 200 mg à t=0, temps en minutes : Cmax et Tmax.

Why: wrong decision: auc_method

- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC linear-up/log-down, dose 200 mg, bolus intraveineux) :
- Cmax : 7078 ng/mL
- Tmax : 19 min
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-043 (ex20_iv_infusion, turn 1; tags: infusion, abbreviation)

Request: Perfusion IV de 150 mg sur 2 h, CL et Vz svp.

Why: wrong decision: auc_method; tag that broke: infusion

- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC linear-up/log-down, dose 150 mg, perfusion intraveineuse de 2 h) :
- CL (clairance) : 0.00405667 dose unit/(h*ng/mL), soit 4.05667 L/h (conversion faite par Caladrius avec la dose en mg)
- Vz (volume de distribution) : 0.0720215 dose unit/(ng/mL), soit 72.0215 L (conversion faite par Caladrius avec la dose en mg)
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-044 (ex21_oral_0, turn 1; tags: dose-unit-micro, route-implied)

Request: Comprimé à libération prolongée de 5000 µg : Cmax, Tmax et demi-vie.

Why: wrong decision: auc_method, route; refused / asked (ask) where the gold decisions expect an answer; tag that broke: dose-unit-micro

- `auc_method`: gold linear, predicted not_applicable
- `route`: gold oral, predicted unknown

Answer:

```text
Je ne lance pas l'analyse : la voie d'administration n'est pas indiquée. Précisez-la (bolus intraveineux, perfusion intraveineuse avec sa durée, ou voie orale).
```

### ood-046 (ex24_pk2_iv_bolus, turn 1; tags: terminology-mismatch, abbreviation)

Request: Bolus de 150 mg : le Cl/F et le Vz/F ?

Why: wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: terminology-mismatch

- `analysis`: gold nca, predicted none_needed
- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, la voie et la méthode d'AUC).
```

### ood-047 (ex25_oral_1, turn 1; tags: abbreviation, unicode)

Request: Voie orale, 100 mg : λz et t½.

Why: wrong decision: auc_method; tag that broke: unicode

- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC linear-up/log-down, dose 100 mg, voie orale (extravasculaire)) :
- λz (constante d'élimination terminale) : 0.0819325 1/h
- t½ (demi-vie terminale) : 8.45998 h
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-048 (ex04_oral_1_lag, turn 1; tags: parameter-not-in-schema)

Request: Voie orale, 300 mg : quelle est la constante d'absorption ka ?

Why: wrong decision: auc_method, is_not_available; tag that broke: parameter-not-in-schema

- `auc_method`: gold linear, predicted not_applicable
- `is_not_available`: gold true, predicted false

Answer:

```text
Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, la voie et la méthode d'AUC).
```

### ood-049 (ex06_oral_0, turn 1; tags: route-stated)

Request: Cmax et nombre de points de la régression terminale, dose orale de 100 mg.

Why: wrong decision: auc_method

- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC linear-up/log-down, dose 100 mg, voie orale (extravasculaire)) :
- Cmax : 595.7 ng/mL
- Nombre de points de la régression terminale : 3
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-051 (ex07_iv_bolus, turn 1; tags: blq, colloquial, dose-unit-micro)

Request: Bolus de 2000 µg : l'AUC(0-t) tient-elle compte du point sous la LLOQ ? et le % extrapolé ?

Why: wrong decision: analysis, asked_c0; refused / asked (no-analysis) where the gold decisions expect an answer

- `analysis`: gold nca, predicted none_needed
- `asked_c0`: gold false, predicted true

Answer:

```text
Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, la voie et la méthode d'AUC).
```

### ood-053 (ex02_oral_1, turn 1; tags: route-missing)

Request: Voici mes concentrations après 400 mg ; quel est le Cmax ?

Why: wrong decision: analysis, auc_method; tag that broke: route-missing

- `analysis`: gold nca, predicted none_needed
- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, la voie et la méthode d'AUC).
```

### ood-054 (ex01_iv_bolus, turn 1; tags: route-implied, c0)

Request: Après une injection intraveineuse directe de 200 mg : C0 et Vz.

Why: wrong decision: auc_method

- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC linear-up/log-down, dose 200 mg, bolus intraveineux) :
- C0 (concentration initiale extrapolée) : 4.38173 mg/L
- Vz (volume de distribution) : 42.4968 dose unit/(mg/L)
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-055 (ex12_iv_infusion, turn 1; tags: infusion, dose-unit-micro)

Request: Perfusion de 500 µg sur 90 min : Cmax.

Why: wrong decision: analysis, auc_method, route; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: infusion

- `analysis`: gold nca, predicted none_needed
- `auc_method`: gold linear, predicted not_applicable
- `route`: gold iv_infusion, predicted unknown

Answer:

```text
Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, la voie et la méthode d'AUC).
```

### ood-056 (ex02_oral_1, turn 2; tags: recall)

Request: Rappelle-moi la dose et la méthode d'AUC utilisées.

Why: wrong decision: auc_method; tag that broke: recall

- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Réglages de l'analyse 2 tels que Caladrius les a enregistrés :
- Dose : 400 mg (unité de votre premier message ; Caladrius a reçu la dose sans unité)
- Voie d'administration : voie orale (extravasculaire)
- Méthode d'AUC : trapèzes linéaires (linear)
```

### ood-057 (ex03_pk2_iv_bolus, turn 2; tags: compare, non-auc-parameter)

Request: Compare le Cmax entre les deux méthodes.

Why: wrong decision: auc_method; tag that broke: compare; tag that broke: non-auc-parameter

- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Comparaison calculée par Caladrius entre l'analyse 2 et l'analyse 3 (b - a ; a = analyse 2, la référence ; b = analyse 3, comparée à la référence) :
- Cmax, méthode linéaire (analyse 2) : 8.391 mg/L
- Cmax, méthode linear-up/log-down (analyse 3) : 8.391 mg/L
- Différence (b - a) : 0 mg/L
- Différence relative : 0 %
- Rapport b/a : 1
```

### ood-058 (ex02_oral_1, turn 1; tags: compare, no-prior-analysis)

Request: Compare les AUC linéaire et lin-up/log-down, dose orale de 400 mg.

Why: refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: compare; tag that broke: no-prior-analysis


Answer:

```text
Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, la voie et la méthode d'AUC).
```

### ood-059 (oodx01_oral_mg_ugml, turn 1; tags: invented, unit-variety, latin-route)

Request: 250 mg per os, voici les concentrations en µg/mL : Cmax, Tmax et AUC0-inf.

Why: wrong decision: asked_auclast; tag that broke: invented; tag that broke: unit-variety

- `asked_auclast`: gold false, predicted true

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC trapèzes linéaires (linear), dose 250 mg, voie orale (extravasculaire)) :
- Cmax : 4.8014 µg/mL
- Tmax : 3 h
- AUC(0-tlast) : 53.7361 h*ug/mL
- AUC(0-inf) : 57.4771 h*ug/mL
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-060 (oodx02_iv_bolus_tlag, turn 1; tags: invented, parameter-not-for-route)

Request: Bolus IV de 120 mg : quel est le Tlag ?

Why: wrong decision: auc_method, is_not_available; tag that broke: invented; tag that broke: parameter-not-for-route

- `auc_method`: gold linear, predicted not_applicable
- `is_not_available`: gold true, predicted false

Answer:

```text
Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, la voie et la méthode d'AUC).
```

### ood-061 (oodx03_oral_c0, turn 1; tags: invented, parameter-not-for-route)

Request: Quelle est la C0 après cette prise orale de 200 mg ?

Why: wrong decision: analysis, auc_method, is_not_available; answered where the gold decisions expect a refusal; tag that broke: invented; tag that broke: parameter-not-for-route

- `analysis`: gold none_needed, predicted nca
- `auc_method`: gold linear, predicted not_applicable
- `is_not_available`: gold true, predicted false

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC linear-up/log-down, dose 200 mg, voie orale (extravasculaire)) :
C0 (concentration initiale extrapolée) n'est pas calculé par Caladrius (« not defined for this route of administration »).
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-062 (oodx04_infusion_dur_h, turn 1; tags: invented, duration-unit-mismatch, infusion)

Request: Perfusion de 75 mg sur 1,5 h, les temps sont en minutes : Cmax.

Why: wrong decision: analysis, auc_method, route; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: invented; tag that broke: duration-unit-mismatch; tag that broke: infusion

- `analysis`: gold nca, predicted none_needed
- `auc_method`: gold linear, predicted not_applicable
- `route`: gold iv_infusion, predicted unknown

Answer:

```text
Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, la voie et la méthode d'AUC).
```

### ood-063 (oodx05_two_subjects, turn 1; tags: invented, multi-subject)

Request: Étude à deux sujets, 300 mg par voie orale : Cmax et AUC0-t par sujet.

Why: tag that broke: invented; tag that broke: multi-subject


Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC trapèzes linéaires (linear), dose 300 mg, voie orale (extravasculaire)) :
Sujet 1 :
- Cmax : 5213 ng/mL
- AUC(0-tlast) : 53632 h*ng/mL
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
Sujet 2 :
- Cmax : 6244.6 ng/mL
- AUC(0-tlast) : 72475.2 h*ng/mL
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-064 (oodx06_steady_state, turn 1; tags: invented, out-of-scope, steady-state, multiple-dose)

Request: Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin.

Why: wrong decision: analysis, asked_cmax, is_not_available, route; tag that broke: invented; tag that broke: out-of-scope; tag that broke: steady-state; tag that broke: multiple-dose

- `analysis`: gold none_needed, predicted not_supported
- `asked_cmax`: gold false, predicted true
- `is_not_available`: gold true, predicted false
- `route`: gold oral, predicted unknown

Answer:

```text
Cette demande (hors du périmètre du harnais) n'est pas prise en charge : le harnais de décision sait lancer une analyse non compartimentale, en donner les paramètres usuels (Cmax, Tmax, C0, AUC, λz, t½, CL, Vz, MRT, Tlag...), rappeler ses réglages et comparer deux analyses ; il ne fait rien d'autre (ni bioéquivalence, ni modèle de population, ni état d'équilibre, ni excrétion urinaire, ni explication rédigée). Je ne donne aucune valeur.
```

### ood-065 (oodx07_urine, turn 1; tags: invented, out-of-scope, urine)

Request: Recueil urinaire : quantité excrétée et clairance rénale.

Why: wrong decision: analysis, asked_cl, dose_has_unit, is_not_available; tag that broke: out-of-scope; tag that broke: urine

- `analysis`: gold none_needed, predicted not_supported
- `asked_cl`: gold false, predicted true
- `dose_has_unit`: gold false, predicted true
- `is_not_available`: gold true, predicted false

Answer:

```text
Cette demande (hors du périmètre du harnais) n'est pas prise en charge : le harnais de décision sait lancer une analyse non compartimentale, en donner les paramètres usuels (Cmax, Tmax, C0, AUC, λz, t½, CL, Vz, MRT, Tlag...), rappeler ses réglages et comparer deux analyses ; il ne fait rien d'autre (ni bioéquivalence, ni modèle de population, ni état d'équilibre, ni excrétion urinaire, ni explication rédigée). Je ne donne aucune valeur.
```

### ood-067 (oodx09_oral_min_ng, turn 1; tags: invented, abbreviation, unit-in-text)

Request: Voie orale 1200 mg, temps en minutes : t1/2 et MRT.

Why: wrong decision: auc_method

- `auc_method`: gold linear, predicted not_applicable

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC linear-up/log-down, dose 1200 mg, voie orale (extravasculaire)) :
- t½ (demi-vie terminale) : 4.95105 min
- MRT (temps moyen de résidence) : 32.3042 min
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-068 (oodx10_oral_blq, turn 1; tags: invented, blq, latin-route)

Request: 80 mg per os, il y a des zéros sous la LLOQ : AUC(0-t) et Cmax.

Why: wrong decision: analysis; refused / asked (no-analysis) where the gold decisions expect an answer

- `analysis`: gold nca, predicted none_needed

Answer:

```text
Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, la voie et la méthode d'AUC).
```

### ood-069 (oodx11_oral_dose_g, turn 1; tags: invented, dose-unit-g, unit-in-text)

Request: J'ai pris 0,25 g par voie orale : Cmax et AUC0-t.

Why: wrong decision: dose_has_unit; answered where the gold decisions expect a refusal; tag that broke: dose-unit-g

- `dose_has_unit`: gold false, predicted true

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC trapèzes linéaires (linear), dose 0.25 g, voie orale (extravasculaire)) :
- Cmax : 7.0537 mg/L
- AUC(0-tlast) : 74.0398 h*mg/L
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-070 (oodx12_iv_infusion_mcg, turn 1; tags: invented, dose-unit-micro, infusion)

Request: Perfusion de 750 µg sur 1 h : Vz et CL.

Why: wrong decision: analysis, auc_method, route; refused / asked (no-analysis) where the gold decisions expect an answer

- `analysis`: gold nca, predicted none_needed
- `auc_method`: gold linear, predicted not_applicable
- `route`: gold iv_infusion, predicted unknown

Answer:

```text
Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, la voie et la méthode d'AUC).
```

### ood-071 (oodx01_oral_mg_ugml, turn 2; tags: invented, compare, rerun)

Request: Compare l'AUC linéaire et la lin-up/log-down.

Why: wrong decision: asked_auclast; tag that broke: rerun

- `asked_auclast`: gold true, predicted false

Answer:

```text
Comparaison calculée par Caladrius entre l'analyse 2 et l'analyse 3 (b - a ; a = analyse 2, la référence ; b = analyse 3, comparée à la référence) :
- Cmax : analyse 2 4.8014 µg/mL ; analyse 3 4.8014 µg/mL ; différence 0 µg/mL ; différence relative 0 % ; rapport b/a 1
- Tmax : analyse 2 3 h ; analyse 3 3 h ; différence 0 h ; différence relative 0 % ; rapport b/a 1
- tfirst : analyse 2 0.5 h ; analyse 3 0.5 h ; différence 0 h ; différence relative 0 % ; rapport b/a 1
- Tlag (temps de latence) : analyse 2 0.5 h ; analyse 3 0.5 h ; différence 0 h ; différence relative 0 % ; rapport b/a 1
- tlast : analyse 2 24 h ; analyse 3 24 h ; différence 0 h ; différence relative 0 % ; rapport b/a 1
- clast.obs : analyse 2 0.44169 µg/mL ; analyse 3 0.44169 µg/mL ; différence 0 µg/mL ; différence relative 0 % ; rapport b/a 1
- AUC(0-tlast) : analyse 2 53.7361 h*ug/mL ; analyse 3 51.5972 h*ug/mL ; différence -2.13895 h*ug/mL ; différence relative -3.98046 % ; rapport b/a 0.960195
- aucall : analyse 2 53.7361 h*ug/mL ; analyse 3 51.5972 h*ug/mL ; différence -2.13895 h*ug/mL ; différence relative -3.98046 % ; rapport b/a 0.960195
- aumclast : analyse 2 408.066 h^2*ug/mL ; analyse 3 409.525 h^2*ug/mL ; différence 1.4596 h^2*ug/mL ; différence relative 0.357687 % ; rapport b/a 1.00358
- aumcall : analyse 2 408.066 h^2*ug/mL ; analyse 3 409.525 h^2*ug/mL ; différence 1.4596 h^2*ug/mL ; différence relative 0.357687 % ; rapport b/a 1.00358
- λz (constante d'élimination terminale) : analyse 2 0.118068 [...]
```

### ood-072 (oodx09_oral_min_ng, turn 2; tags: invented, compare, by-id)

Request: Compare l'analyse 2 et l'analyse 1 pour l'AUC.

Why: wrong decision: asked_auclast, auc_method, compare_pair; tag that broke: by-id

- `asked_auclast`: gold true, predicted false
- `auc_method`: gold lin_up_log_down, predicted not_applicable
- `compare_pair`: gold 3+2, predicted 2+3

Answer:

```text
Comparaison calculée par Caladrius entre l'analyse 2 et l'analyse 3 (b - a ; a = analyse 2, la référence ; b = analyse 3, comparée à la référence) :
- Cmax : analyse 2 436.23 ng/mL ; analyse 3 436.23 ng/mL ; différence 0 ng/mL ; différence relative 0 % ; rapport b/a 1
- Tmax : analyse 2 30 min ; analyse 3 30 min ; différence 0 min ; différence relative 0 % ; rapport b/a 1
- tfirst : analyse 2 30 min ; analyse 3 30 min ; différence 0 min ; différence relative 0 % ; rapport b/a 1
- tlast : analyse 2 1440 min ; analyse 3 1440 min ; différence 0 min ; différence relative 0 % ; rapport b/a 1
- clast.obs : analyse 2 8.1281e-84 ng/mL ; analyse 3 8.1281e-84 ng/mL ; différence 0 ng/mL ; différence relative 0 % ; rapport b/a 1
- AUC(0-tlast) : analyse 2 13286.2 min*ng/mL ; analyse 3 9659.39 min*ng/mL ; différence -3626.77 min*ng/mL ; différence relative -27.2974 % ; rapport b/a 0.727026
- aucall : analyse 2 13286.2 min*ng/mL ; analyse 3 9659.39 min*ng/mL ; différence -3626.77 min*ng/mL ; différence relative -27.2974 % ; rapport b/a 0.727026
- aumclast : analyse 2 404655 min^2*ng/mL ; analyse 3 312038 min^2*ng/mL ; différence -92616.3 min^2*ng/mL ; différence relative -22.8877 % ; rapport b/a 0.771123
- aumcall : analyse 2 404655 min^2*ng/mL ; analyse 3 312038 min^2*ng/mL ; différence -92616.3 min^2*ng/mL ; différence relative -22.8877 % ; rapport b/a 0.771123
- λz (constante d'élimination terminale) : analyse 2 0.14 1/min ; analyse 3 0.14 1/min ; différence 0 1/min ; différence relativ [...]
```

### ood-073 (oodx03_oral_c0, turn 1; tags: invented, plain)

Request: Prise orale de 200 mg : Cmax, Tmax et AUC0-t.

Why: tag that broke: plain


Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC trapèzes linéaires (linear), dose 200 mg, voie orale (extravasculaire)) :
- Cmax : 3768.2 ng/mL
- Tmax : 2 h
- AUC(0-tlast) : 39105.1 h*ng/mL
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```

### ood-074 (oodx02_iv_bolus_tlag, turn 1; tags: invented, plain)

Request: Bolus de 120 mg : Cmax et AUC0-inf.

Why: wrong decision: asked_auclast; tag that broke: plain

- `asked_auclast`: gold false, predicted true

Answer:

```text
Résultats de Caladrius (analyse 2, méthode d'AUC trapèzes linéaires (linear), dose 120 mg, bolus intraveineux) :
- Cmax : 5.2657 mg/L
- AUC(0-tlast) : 31.799 h*mg/L
- AUC(0-inf) : 38.9357 h*mg/L
Avertissement de Caladrius : « the dose has no unit; derived units (AUC, clearance, volume) cannot be named ».
```


## Decision model

- model: C:\Users\abdou\apothicaire\agent\decision\models\qwen35-0.8b-d01-v2\adapters
- load_s: 8.7
- decide_calls: 151
- model_seconds_total: 35.13
- model_seconds_per_call: 0.2327
- torch_peak_allocated_mib: 1437
- nvidia_smi_used_mib_at_end: 2325
