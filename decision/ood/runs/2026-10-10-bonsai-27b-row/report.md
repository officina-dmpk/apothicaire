# Out-of-distribution requests: decider `bonsai-27b-row`, 2026-10-10

`decision/eval_ood.py`; 74 requests converted from `decision/ood/requests.jsonl` (schema report: `decision/ood/schema_report.md`).

## Scoring on the rows

74 rows, 1480 decisions: **91.8 %** correct overall; 7 of 74 rows have all their decisions right (9.5 %). Always-majority on these rows: 86.6 %; majority learned on train.jsonl: 81.4 %.

### Accuracy per question

| question | correct | total | accuracy | always-majority (these rows) | majority (train.jsonl) |
|---|---|---|---|---|---|
| analysis | 51 | 74 | 68.9 % | 60.8 % | 21.6 % |
| asked_adj_r2 | 74 | 74 | 100.0 % | 98.6 % | 98.6 % |
| asked_aucinf | 73 | 74 | 98.6 % | 91.9 % | 91.9 % |
| asked_auclast | 59 | 74 | 79.7 % | 73.0 % | 73.0 % |
| asked_aucpext | 74 | 74 | 100.0 % | 95.9 % | 95.9 % |
| asked_c0 | 74 | 74 | 100.0 % | 95.9 % | 95.9 % |
| asked_cl | 73 | 74 | 98.6 % | 87.8 % | 87.8 % |
| asked_cmax | 73 | 74 | 98.6 % | 70.3 % | 70.3 % |
| asked_half_life | 74 | 74 | 100.0 % | 87.8 % | 87.8 % |
| asked_lambda_z | 74 | 74 | 100.0 % | 98.6 % | 98.6 % |
| asked_lambda_z_points | 74 | 74 | 100.0 % | 97.3 % | 97.3 % |
| asked_mrt | 74 | 74 | 100.0 % | 95.9 % | 95.9 % |
| asked_tlag | 74 | 74 | 100.0 % | 94.6 % | 94.6 % |
| asked_tmax | 74 | 74 | 100.0 % | 90.5 % | 90.5 % |
| asked_vz | 73 | 74 | 98.6 % | 87.8 % | 87.8 % |
| auc_method | 14 | 74 | 18.9 % | 77.0 % | 12.2 % |
| compare_pair | 71 | 74 | 95.9 % | 94.6 % | 94.6 % |
| dose_has_unit | 72 | 74 | 97.3 % | 93.2 % | 93.2 % |
| is_not_available | 63 | 74 | 85.1 % | 85.1 % | 85.1 % |
| route | 70 | 74 | 94.6 % | 54.1 % | 54.1 % |
| **overall** | 1358 | 1480 | **91.8 %** | 86.6 % | 81.4 % |

### Confusions (wrong cells only: gold -> predicted, count)

- `analysis`: none_needed -> fit_pk2 (8); nca -> fit_pk2 (7); nca -> fit_pk1 (4); none_needed -> nca (2); compare -> nca (1); none_needed -> fit_pk1 (1).
- `route`: oral -> unknown (4).
- `auc_method`: linear -> not_applicable (55); lin_up_log_down -> not_applicable (5).
- `compare_pair`: not_applicable -> none_available (3).
- `is_not_available`: true -> false (11).
- `dose_has_unit`: false -> true (2).
- `asked_<parameter>` (14 questions): 15 parameters asked and missed (of 99 asked), 4 parameters predicted asked that were not.

### Accuracy per tag (which kinds of hard requests break)

| tag | rows | decisions correct | accuracy | rows all right |
|---|---|---|---|---|
| bioequivalence | 1 | 16/20 | 80.0 % | 0.0 % |
| blq | 4 | 73/80 | 91.2 % | 0.0 % |
| by-id | 2 | 37/40 | 92.5 % | 0.0 % |
| c0 | 1 | 18/20 | 90.0 % | 0.0 % |
| colloquial | 6 | 109/120 | 90.8 % | 0.0 % |
| compare | 8 | 144/160 | 90.0 % | 0.0 % |
| dose-unit-g | 1 | 17/20 | 85.0 % | 0.0 % |
| dose-unit-mcg | 1 | 18/20 | 90.0 % | 0.0 % |
| dose-unit-mg | 1 | 19/20 | 95.0 % | 0.0 % |
| dose-unit-micro | 9 | 165/180 | 91.7 % | 0.0 % |
| dose-without-unit | 1 | 19/20 | 95.0 % | 0.0 % |
| duration-unit-mismatch | 2 | 38/40 | 95.0 % | 0.0 % |
| duration-word | 1 | 18/20 | 90.0 % | 0.0 % |
| english-term | 1 | 18/20 | 90.0 % | 0.0 % |
| follow-up | 4 | 76/80 | 95.0 % | 0.0 % |
| infusion | 7 | 129/140 | 92.1 % | 0.0 % |
| iv-explicit | 1 | 17/20 | 85.0 % | 0.0 % |
| latin-route | 3 | 56/60 | 93.3 % | 0.0 % |
| multi-subject | 1 | 18/20 | 90.0 % | 0.0 % |
| multiple-dose | 1 | 16/20 | 80.0 % | 0.0 % |
| no-dose | 1 | 18/20 | 90.0 % | 0.0 % |
| no-parameter | 1 | 19/20 | 95.0 % | 0.0 % |
| no-prior-analysis | 1 | 15/20 | 75.0 % | 0.0 % |
| non-auc-parameter | 1 | 19/20 | 95.0 % | 0.0 % |
| out-of-scope | 4 | 66/80 | 82.5 % | 0.0 % |
| parameter-not-for-route | 5 | 85/100 | 85.0 % | 0.0 % |
| parameter-not-in-schema | 2 | 33/40 | 82.5 % | 0.0 % |
| plain | 2 | 37/40 | 92.5 % | 0.0 % |
| population | 1 | 17/20 | 85.0 % | 0.0 % |
| rerun | 4 | 74/80 | 92.5 % | 0.0 % |
| route-implied | 5 | 92/100 | 92.0 % | 0.0 % |
| route-missing | 1 | 19/20 | 95.0 % | 0.0 % |
| route-stated | 8 | 147/160 | 91.9 % | 0.0 % |
| steady-state | 1 | 16/20 | 80.0 % | 0.0 % |
| terminology-mismatch | 2 | 38/40 | 95.0 % | 0.0 % |
| tlag | 1 | 18/20 | 90.0 % | 0.0 % |
| two-requests-in-one-sentence | 2 | 38/40 | 95.0 % | 0.0 % |
| typo | 2 | 38/40 | 95.0 % | 0.0 % |
| unicode | 1 | 18/20 | 90.0 % | 0.0 % |
| unit-conversion-in-text | 1 | 19/20 | 95.0 % | 0.0 % |
| unit-in-text | 5 | 91/100 | 91.0 % | 0.0 % |
| unit-variety | 1 | 19/20 | 95.0 % | 0.0 % |
| unrecognized-unit | 1 | 18/20 | 90.0 % | 0.0 % |
| urine | 1 | 17/20 | 85.0 % | 0.0 % |
| abbreviation | 17 | 316/340 | 92.9 % | 5.9 % |
| invented | 16 | 288/320 | 90.0 % | 6.2 % |
| language-mix | 2 | 39/40 | 97.5 % | 50.0 % |
| method-explicit | 2 | 39/40 | 97.5 % | 50.0 % |
| fit | 4 | 80/80 | 100.0 % | 100.0 % |
| oral | 1 | 20/20 | 100.0 % | 100.0 % |
| recall | 1 | 20/20 | 100.0 % | 100.0 % |
| simulate | 1 | 20/20 | 100.0 % | 100.0 % |
| two-compartments | 2 | 40/40 | 100.0 % | 100.0 % |

Tags that broke (share of fully correct rows below the overall share): abbreviation, bioequivalence, blq, by-id, c0, colloquial, compare, dose-unit-g, dose-unit-mcg, dose-unit-mg, dose-unit-micro, dose-without-unit, duration-unit-mismatch, duration-word, english-term, follow-up, infusion, invented, iv-explicit, latin-route, multi-subject, multiple-dose, no-dose, no-parameter, no-prior-analysis, non-auc-parameter, out-of-scope, parameter-not-for-route, parameter-not-in-schema, plain, population, rerun, route-implied, route-missing, route-stated, steady-state, terminology-mismatch, tlag, two-requests-in-one-sentence, typo, unicode, unit-conversion-in-text, unit-in-text, unit-variety, unrecognized-unit, urine.

### Calibration (probability of the chosen label vs observed accuracy)

The decider gives labels without probabilities: no calibration table.

### Wrong decisions (122)

| row | question | gold | predicted | confidence | request |
|---|---|---|---|---|---|
| ood-001 | auc_method | linear | not_applicable | - | J'ai pris un comprimé de 400 mg ce matin, voici mes concentrations. C'est quoi le Cmax et le Tmax ? |
| ood-002 | auc_method | linear | not_applicable | - | et la t1/2 stp ? |
| ood-003 | auc_method | linear | not_applicable | - | AUC0-t et AUC0-inf svp |
| ood-004 | analysis | nca | fit_pk1 | - | bolus IV de 200 mg ; quel est le Vd ? |
| ood-004 | auc_method | linear | not_applicable | - | bolus IV de 200 mg ; quel est le Vd ? |
| ood-005 | auc_method | linear | not_applicable | - | bolus de 200 mg : Cl/F ? |
| ood-008 | asked_auclast | true | false | - | Perfusion de 150 mg sur 2 h. Donne-moi le Cmax et l'AUC(0-t). |
| ood-008 | auc_method | linear | not_applicable | - | Perfusion de 150 mg sur 2 h. Donne-moi le Cmax et l'AUC(0-t). |
| ood-009 | auc_method | linear | not_applicable | - | Et la MRT ? |
| ood-010 | auc_method | linear | not_applicable | - | Perfusion de 500 µg pendant 1,5 h, Cmax et AUC0-inf. |
| ood-011 | asked_auclast | true | false | - | Perfusion de 500 µg pendant 90 minutes : que vaut l'AUC(0-t) ? |
| ood-011 | auc_method | linear | not_applicable | - | Perfusion de 500 µg pendant 90 minutes : que vaut l'AUC(0-t) ? |
| ood-012 | asked_auclast | true | false | - | J'ai avalé 800 µg, les temps sont en minutes ; Cmax et AUC0-t. |
| ood-012 | auc_method | linear | not_applicable | - | J'ai avalé 800 µg, les temps sont en minutes ; Cmax et AUC0-t. |
| ood-013 | asked_auclast | true | false | - | Compare l'AUC linéaire et la lin-up/log-down. |
| ood-013 | auc_method | lin_up_log_down | not_applicable | - | Compare l'AUC linéaire et la lin-up/log-down. |
| ood-014 | asked_auclast | true | false | - | Compare les deux AUC (valeur et %). |
| ood-014 | auc_method | linear | not_applicable | - | Compare les deux AUC (valeur et %). |
| ood-015 | auc_method | lin_up_log_down | not_applicable | - | Compare l'analyse 2 à l'analyse 1. |
| ood-016 | analysis | nca | fit_pk2 | - | Voie orale, 300 mg : y a-t-il un Tlag ? |
| ood-016 | auc_method | linear | not_applicable | - | Voie orale, 300 mg : y a-t-il un Tlag ? |
| ood-017 | analysis | none_needed | fit_pk2 | - | Quel est le Tlag de ce bolus de 200 mg ? |
| ood-017 | auc_method | linear | not_applicable | - | Quel est le Tlag de ce bolus de 200 mg ? |
| ood-017 | is_not_available | true | false | - | Quel est le Tlag de ce bolus de 200 mg ? |
| ood-018 | analysis | none_needed | fit_pk2 | - | Quelle est la C0 après cette prise orale de 400 mg ? |
| ood-018 | auc_method | linear | not_applicable | - | Quelle est la C0 après cette prise orale de 400 mg ? |
| ood-018 | is_not_available | true | false | - | Quelle est la C0 après cette prise orale de 400 mg ? |
| ood-019 | analysis | none_needed | nca | - | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-019 | compare_pair | not_applicable | none_available | - | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-019 | is_not_available | true | false | - | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-019 | route | oral | unknown | - | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-020 | analysis | none_needed | fit_pk2 | - | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. |
| ood-020 | is_not_available | true | false | - | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. |
| ood-020 | route | oral | unknown | - | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. |
| ood-021 | analysis | nca | fit_pk2 | - | Après une prise orale, voici mes concentrations : quelle est la demi-vie ? |
| ood-021 | auc_method | linear | not_applicable | - | Après une prise orale, voici mes concentrations : quelle est la demi-vie ? |
| ood-022 | auc_method | linear | not_applicable | - | Prise orale de 100, voici les données. Cmax ? |
| ood-023 | auc_method | linear | not_applicable | - | Bolus IV de 2 mg : donne-moi la clairance et le Vz. |
| ood-024 | auc_method | linear | not_applicable | - | Bolus de 2000 mcg : CL et Vz. |
| ood-024 | dose_has_unit | false | true | - | Bolus de 2000 mcg : CL et Vz. |
| ood-025 | auc_method | linear | not_applicable | - | Et le pourcentage d'AUC extrapolée ? |
| ood-026 | auc_method | linear | not_applicable | - | Il y a un zéro sous la LLOQ dans le tableau, on le garde ? Donne l'AUC(0-t) et la Cmax, dose orale 50 mg. |
| ood-028 | auc_method | linear | not_applicable | - | Donne-moi d'abord la demi-vie, ensuite la clairance et le Vz, pour cette dose orale de 300 mg. |
| ood-029 | analysis | nca | fit_pk2 | - | Donne-moi le Cmax puis refais l'analyse en lin-up/log-down, bolus de 300 mg. |
| ood-030 | asked_auclast | true | false | - | Refais l'analyse en lin-up/log-down et compare les deux AUC en valeur et en %. |
| ood-031 | auc_method | linear | not_applicable | - | Peux-tu me donner le Cmax, le Tmax et le t1/2 after a single oral dose of 100 mg ? |
| ood-032 | auc_method | linear | not_applicable | - | kel est le Cmax é le Tmax de ce tablo ? dose 400 mg per os |
| ood-033 | auc_method | linear | not_applicable | - | Dose orale de 500 mg : AUC0-∞ et AUC0-t. |
| ood-034 | analysis | none_needed | fit_pk1 | - | Bolus de 150 mg : quel est le Vdss ? |
| ood-034 | asked_vz | false | true | - | Bolus de 150 mg : quel est le Vdss ? |
| ood-034 | auc_method | linear | not_applicable | - | Bolus de 150 mg : quel est le Vdss ? |
| ood-034 | is_not_available | true | false | - | Bolus de 150 mg : quel est le Vdss ? |
| ood-035 | analysis | nca | fit_pk1 | - | Bolus de 150 mg : le R² ajusté et le nombre de points de la régression terminale. |
| ood-035 | auc_method | linear | not_applicable | - | Bolus de 150 mg : le R² ajusté et le nombre de points de la régression terminale. |
| ood-036 | auc_method | linear | not_applicable | - | Prise unique de 100 mg par voie orale : je veux le MRT et la demi-vie. |
| ood-037 | analysis | nca | fit_pk2 | - | Perfusion de 150 mg sur 2 h : clairance et volume de distribution. |
| ood-037 | auc_method | linear | not_applicable | - | Perfusion de 150 mg sur 2 h : clairance et volume de distribution. |
| ood-038 | analysis | none_needed | fit_pk2 | - | Quel est le Tlag de cette perfusion de 150 mg ? |
| ood-038 | auc_method | linear | not_applicable | - | Quel est le Tlag de cette perfusion de 150 mg ? |
| ood-038 | is_not_available | true | false | - | Quel est le Tlag de cette perfusion de 150 mg ? |
| ood-039 | auc_method | linear | not_applicable | - | Dose IV de 1000 µg : AUC(0-inf) et pourcentage extrapolé. |
| ood-040 | analysis | nca | fit_pk2 | - | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? |
| ood-040 | auc_method | linear | not_applicable | - | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? |
| ood-040 | route | oral | unknown | - | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? |
| ood-041 | analysis | nca | fit_pk1 | - | Bolus de 200 mg à t=0, temps en minutes : Cmax et Tmax. |
| ood-041 | auc_method | linear | not_applicable | - | Bolus de 200 mg à t=0, temps en minutes : Cmax et Tmax. |
| ood-043 | auc_method | linear | not_applicable | - | Perfusion IV de 150 mg sur 2 h, CL et Vz svp. |
| ood-044 | auc_method | linear | not_applicable | - | Comprimé à libération prolongée de 5000 µg : Cmax, Tmax et demi-vie. |
| ood-045 | auc_method | linear | not_applicable | - | Bolus de 300 mg, temps en minutes : AUC(0-t) et clairance. |
| ood-046 | auc_method | linear | not_applicable | - | Bolus de 150 mg : le Cl/F et le Vz/F ? |
| ood-047 | analysis | nca | fit_pk2 | - | Voie orale, 100 mg : λz et t½. |
| ood-047 | auc_method | linear | not_applicable | - | Voie orale, 100 mg : λz et t½. |
| ood-048 | analysis | none_needed | fit_pk2 | - | Voie orale, 300 mg : quelle est la constante d'absorption ka ? |
| ood-048 | auc_method | linear | not_applicable | - | Voie orale, 300 mg : quelle est la constante d'absorption ka ? |
| ood-048 | is_not_available | true | false | - | Voie orale, 300 mg : quelle est la constante d'absorption ka ? |
| ood-049 | auc_method | linear | not_applicable | - | Cmax et nombre de points de la régression terminale, dose orale de 100 mg. |
| ood-050 | asked_auclast | true | false | - | AUC(0-t) par la méthode lin-up/log-down, dose orale de 50 mg. |
| ood-051 | asked_auclast | true | false | - | Bolus de 2000 µg : l'AUC(0-t) tient-elle compte du point sous la LLOQ ? et le % extrapolé ? |
| ood-051 | auc_method | linear | not_applicable | - | Bolus de 2000 µg : l'AUC(0-t) tient-elle compte du point sous la LLOQ ? et le % extrapolé ? |
| ood-051 | compare_pair | not_applicable | none_available | - | Bolus de 2000 µg : l'AUC(0-t) tient-elle compte du point sous la LLOQ ? et le % extrapolé ? |
| ood-053 | auc_method | linear | not_applicable | - | Voici mes concentrations après 400 mg ; quel est le Cmax ? |
| ood-054 | analysis | nca | fit_pk1 | - | Après une injection intraveineuse directe de 200 mg : C0 et Vz. |
| ood-054 | auc_method | linear | not_applicable | - | Après une injection intraveineuse directe de 200 mg : C0 et Vz. |
| ood-055 | auc_method | linear | not_applicable | - | Perfusion de 500 µg sur 90 min : Cmax. |
| ood-057 | auc_method | linear | not_applicable | - | Compare le Cmax entre les deux méthodes. |
| ood-058 | analysis | compare | nca | - | Compare les AUC linéaire et lin-up/log-down, dose orale de 400 mg. |
| ood-058 | asked_aucinf | false | true | - | Compare les AUC linéaire et lin-up/log-down, dose orale de 400 mg. |
| ood-058 | asked_auclast | true | false | - | Compare les AUC linéaire et lin-up/log-down, dose orale de 400 mg. |
| ood-058 | auc_method | lin_up_log_down | not_applicable | - | Compare les AUC linéaire et lin-up/log-down, dose orale de 400 mg. |
| ood-058 | compare_pair | not_applicable | none_available | - | Compare les AUC linéaire et lin-up/log-down, dose orale de 400 mg. |
| ood-059 | auc_method | linear | not_applicable | - | 250 mg per os, voici les concentrations en µg/mL : Cmax, Tmax et AUC0-inf. |
| ood-060 | analysis | none_needed | fit_pk2 | - | Bolus IV de 120 mg : quel est le Tlag ? |
| ood-060 | auc_method | linear | not_applicable | - | Bolus IV de 120 mg : quel est le Tlag ? |
| ood-060 | is_not_available | true | false | - | Bolus IV de 120 mg : quel est le Tlag ? |
| ood-061 | analysis | none_needed | fit_pk2 | - | Quelle est la C0 après cette prise orale de 200 mg ? |
| ood-061 | auc_method | linear | not_applicable | - | Quelle est la C0 après cette prise orale de 200 mg ? |
| ood-061 | is_not_available | true | false | - | Quelle est la C0 après cette prise orale de 200 mg ? |
| ood-062 | auc_method | linear | not_applicable | - | Perfusion de 75 mg sur 1,5 h, les temps sont en minutes : Cmax. |
| ood-063 | asked_auclast | true | false | - | Étude à deux sujets, 300 mg par voie orale : Cmax et AUC0-t par sujet. |
| ood-063 | auc_method | linear | not_applicable | - | Étude à deux sujets, 300 mg par voie orale : Cmax et AUC0-t par sujet. |
| ood-064 | analysis | none_needed | fit_pk2 | - | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-064 | asked_cmax | false | true | - | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-064 | is_not_available | true | false | - | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-064 | route | oral | unknown | - | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-065 | analysis | none_needed | nca | - | Recueil urinaire : quantité excrétée et clairance rénale. |
| ood-065 | asked_cl | false | true | - | Recueil urinaire : quantité excrétée et clairance rénale. |
| ood-065 | is_not_available | true | false | - | Recueil urinaire : quantité excrétée et clairance rénale. |
| ood-067 | analysis | nca | fit_pk2 | - | Voie orale 1200 mg, temps en minutes : t1/2 et MRT. |
| ood-067 | auc_method | linear | not_applicable | - | Voie orale 1200 mg, temps en minutes : t1/2 et MRT. |
| ood-068 | asked_auclast | true | false | - | 80 mg per os, il y a des zéros sous la LLOQ : AUC(0-t) et Cmax. |
| ood-068 | auc_method | linear | not_applicable | - | 80 mg per os, il y a des zéros sous la LLOQ : AUC(0-t) et Cmax. |
| ood-069 | asked_auclast | true | false | - | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. |
| ood-069 | auc_method | linear | not_applicable | - | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. |
| ood-069 | dose_has_unit | false | true | - | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. |
| ood-070 | auc_method | linear | not_applicable | - | Perfusion de 750 µg sur 1 h : Vz et CL. |
| ood-071 | asked_auclast | true | false | - | Compare l'AUC linéaire et la lin-up/log-down. |
| ood-071 | auc_method | lin_up_log_down | not_applicable | - | Compare l'AUC linéaire et la lin-up/log-down. |
| ood-072 | asked_auclast | true | false | - | Compare l'analyse 2 et l'analyse 1 pour l'AUC. |
| ood-072 | auc_method | lin_up_log_down | not_applicable | - | Compare l'analyse 2 et l'analyse 1 pour l'AUC. |
| ood-073 | asked_auclast | true | false | - | Prise orale de 200 mg : Cmax, Tmax et AUC0-t. |
| ood-073 | auc_method | linear | not_applicable | - | Prise orale de 200 mg : Cmax, Tmax et AUC0-t. |
| ood-074 | auc_method | linear | not_applicable | - | Bolus de 120 mg : Cmax et AUC0-inf. |
