# Out-of-distribution requests: decider `bonsai-27b-question`, 2026-10-10

`decision/eval_ood.py`; 74 requests converted from `decision/ood/requests.jsonl` (schema report: `decision/ood/schema_report.md`).

## Scoring on the rows

74 rows, 1480 decisions: **87.4 %** correct overall; 1 of 74 rows have all their decisions right (1.4 %). Always-majority on these rows: 86.6 %; majority learned on train.jsonl: 81.4 %.

### Accuracy per question

| question | correct | total | accuracy | always-majority (these rows) | majority (train.jsonl) |
|---|---|---|---|---|---|
| analysis | 55 | 74 | 74.3 % | 60.8 % | 21.6 % |
| asked_adj_r2 | 74 | 74 | 100.0 % | 98.6 % | 98.6 % |
| asked_aucinf | 72 | 74 | 97.3 % | 91.9 % | 91.9 % |
| asked_auclast | 64 | 74 | 86.5 % | 73.0 % | 73.0 % |
| asked_aucpext | 73 | 74 | 98.6 % | 95.9 % | 95.9 % |
| asked_c0 | 73 | 74 | 98.6 % | 95.9 % | 95.9 % |
| asked_cl | 72 | 74 | 97.3 % | 87.8 % | 87.8 % |
| asked_cmax | 72 | 74 | 97.3 % | 70.3 % | 70.3 % |
| asked_half_life | 72 | 74 | 97.3 % | 87.8 % | 87.8 % |
| asked_lambda_z | 62 | 74 | 83.8 % | 98.6 % | 98.6 % |
| asked_lambda_z_points | 74 | 74 | 100.0 % | 97.3 % | 97.3 % |
| asked_mrt | 74 | 74 | 100.0 % | 95.9 % | 95.9 % |
| asked_tlag | 73 | 74 | 98.6 % | 94.6 % | 94.6 % |
| asked_tmax | 73 | 74 | 98.6 % | 90.5 % | 90.5 % |
| asked_vz | 72 | 74 | 97.3 % | 87.8 % | 87.8 % |
| auc_method | 17 | 74 | 23.0 % | 77.0 % | 12.2 % |
| compare_pair | 16 | 74 | 21.6 % | 94.6 % | 94.6 % |
| dose_has_unit | 72 | 74 | 97.3 % | 93.2 % | 93.2 % |
| is_not_available | 64 | 74 | 86.5 % | 85.1 % | 85.1 % |
| route | 70 | 74 | 94.6 % | 54.1 % | 54.1 % |
| **overall** | 1294 | 1480 | **87.4 %** | 86.6 % | 81.4 % |

### Confusions (wrong cells only: gold -> predicted, count)

- `analysis`: none_needed -> nca (10); nca -> fit_pk1 (3); compare -> nca (2); compare -> none_needed (2); none_needed -> fit_pk1 (1); none_needed -> fit_pk2 (1).
- `route`: oral -> unknown (4).
- `auc_method`: linear -> not_applicable (54); lin_up_log_down -> not_applicable (2); linear -> lin_up_log_down (1).
- `compare_pair`: not_applicable -> none_available (56); 2+3 -> not_applicable (2).
- `is_not_available`: true -> false (10).
- `dose_has_unit`: false -> true (2).
- `asked_<parameter>` (14 questions): 11 parameters asked and missed (of 99 asked), 25 parameters predicted asked that were not.

### Accuracy per tag (which kinds of hard requests break)

| tag | rows | decisions correct | accuracy | rows all right |
|---|---|---|---|---|
| abbreviation | 17 | 294/340 | 86.5 % | 0.0 % |
| bioequivalence | 1 | 16/20 | 80.0 % | 0.0 % |
| blq | 4 | 73/80 | 91.2 % | 0.0 % |
| by-id | 2 | 33/40 | 82.5 % | 0.0 % |
| c0 | 1 | 18/20 | 90.0 % | 0.0 % |
| colloquial | 6 | 108/120 | 90.0 % | 0.0 % |
| compare | 8 | 141/160 | 88.1 % | 0.0 % |
| dose-unit-g | 1 | 16/20 | 80.0 % | 0.0 % |
| dose-unit-mcg | 1 | 17/20 | 85.0 % | 0.0 % |
| dose-unit-mg | 1 | 19/20 | 95.0 % | 0.0 % |
| dose-unit-micro | 9 | 160/180 | 88.9 % | 0.0 % |
| dose-without-unit | 1 | 18/20 | 90.0 % | 0.0 % |
| duration-unit-mismatch | 2 | 36/40 | 90.0 % | 0.0 % |
| duration-word | 1 | 18/20 | 90.0 % | 0.0 % |
| english-term | 1 | 19/20 | 95.0 % | 0.0 % |
| fit | 4 | 73/80 | 91.2 % | 0.0 % |
| follow-up | 4 | 65/80 | 81.2 % | 0.0 % |
| infusion | 7 | 123/140 | 87.9 % | 0.0 % |
| invented | 16 | 273/320 | 85.3 % | 0.0 % |
| iv-explicit | 1 | 15/20 | 75.0 % | 0.0 % |
| language-mix | 2 | 37/40 | 92.5 % | 0.0 % |
| latin-route | 3 | 55/60 | 91.7 % | 0.0 % |
| method-explicit | 2 | 38/40 | 95.0 % | 0.0 % |
| multi-subject | 1 | 17/20 | 85.0 % | 0.0 % |
| multiple-dose | 1 | 15/20 | 75.0 % | 0.0 % |
| no-dose | 1 | 17/20 | 85.0 % | 0.0 % |
| no-parameter | 1 | 17/20 | 85.0 % | 0.0 % |
| no-prior-analysis | 1 | 16/20 | 80.0 % | 0.0 % |
| non-auc-parameter | 1 | 18/20 | 90.0 % | 0.0 % |
| oral | 1 | 19/20 | 95.0 % | 0.0 % |
| out-of-scope | 4 | 64/80 | 80.0 % | 0.0 % |
| parameter-not-for-route | 5 | 76/100 | 76.0 % | 0.0 % |
| parameter-not-in-schema | 2 | 31/40 | 77.5 % | 0.0 % |
| plain | 2 | 35/40 | 87.5 % | 0.0 % |
| population | 1 | 16/20 | 80.0 % | 0.0 % |
| rerun | 4 | 75/80 | 93.8 % | 0.0 % |
| route-implied | 5 | 90/100 | 90.0 % | 0.0 % |
| route-missing | 1 | 18/20 | 90.0 % | 0.0 % |
| route-stated | 8 | 143/160 | 89.4 % | 0.0 % |
| simulate | 1 | 19/20 | 95.0 % | 0.0 % |
| steady-state | 1 | 15/20 | 75.0 % | 0.0 % |
| terminology-mismatch | 2 | 36/40 | 90.0 % | 0.0 % |
| tlag | 1 | 18/20 | 90.0 % | 0.0 % |
| two-compartments | 2 | 36/40 | 90.0 % | 0.0 % |
| two-requests-in-one-sentence | 2 | 38/40 | 95.0 % | 0.0 % |
| typo | 2 | 37/40 | 92.5 % | 0.0 % |
| unicode | 1 | 17/20 | 85.0 % | 0.0 % |
| unit-conversion-in-text | 1 | 19/20 | 95.0 % | 0.0 % |
| unit-in-text | 5 | 87/100 | 87.0 % | 0.0 % |
| unit-variety | 1 | 18/20 | 90.0 % | 0.0 % |
| unrecognized-unit | 1 | 17/20 | 85.0 % | 0.0 % |
| urine | 1 | 17/20 | 85.0 % | 0.0 % |
| recall | 1 | 20/20 | 100.0 % | 100.0 % |

Tags that broke (share of fully correct rows below the overall share): abbreviation, bioequivalence, blq, by-id, c0, colloquial, compare, dose-unit-g, dose-unit-mcg, dose-unit-mg, dose-unit-micro, dose-without-unit, duration-unit-mismatch, duration-word, english-term, fit, follow-up, infusion, invented, iv-explicit, language-mix, latin-route, method-explicit, multi-subject, multiple-dose, no-dose, no-parameter, no-prior-analysis, non-auc-parameter, oral, out-of-scope, parameter-not-for-route, parameter-not-in-schema, plain, population, rerun, route-implied, route-missing, route-stated, simulate, steady-state, terminology-mismatch, tlag, two-compartments, two-requests-in-one-sentence, typo, unicode, unit-conversion-in-text, unit-in-text, unit-variety, unrecognized-unit, urine.

### Calibration (probability of the chosen label vs observed accuracy)

The decider gives labels without probabilities: no calibration table.

### Wrong decisions (186)

| row | question | gold | predicted | confidence | request |
|---|---|---|---|---|---|
| ood-001 | auc_method | linear | not_applicable | - | J'ai pris un comprimé de 400 mg ce matin, voici mes concentrations. C'est quoi le Cmax et le Tmax ? |
| ood-002 | asked_lambda_z | false | true | - | et la t1/2 stp ? |
| ood-002 | auc_method | linear | not_applicable | - | et la t1/2 stp ? |
| ood-003 | analysis | none_needed | nca | - | AUC0-t et AUC0-inf svp |
| ood-003 | asked_auclast | true | false | - | AUC0-t et AUC0-inf svp |
| ood-003 | asked_aucpext | false | true | - | AUC0-t et AUC0-inf svp |
| ood-003 | auc_method | linear | not_applicable | - | AUC0-t et AUC0-inf svp |
| ood-004 | auc_method | linear | not_applicable | - | bolus IV de 200 mg ; quel est le Vd ? |
| ood-004 | compare_pair | not_applicable | none_available | - | bolus IV de 200 mg ; quel est le Vd ? |
| ood-005 | auc_method | linear | not_applicable | - | bolus de 200 mg : Cl/F ? |
| ood-005 | compare_pair | not_applicable | none_available | - | bolus de 200 mg : Cl/F ? |
| ood-006 | asked_lambda_z | false | true | - | Ajuste un modèle à deux compartiments après un bolus IV de 300 mg. |
| ood-006 | compare_pair | not_applicable | none_available | - | Ajuste un modèle à deux compartiments après un bolus IV de 300 mg. |
| ood-007 | asked_lambda_z | false | true | - | fit un modèle mono-compartiment sur ces données (bolus de 300 mg) |
| ood-007 | compare_pair | not_applicable | none_available | - | fit un modèle mono-compartiment sur ces données (bolus de 300 mg) |
| ood-008 | auc_method | linear | not_applicable | - | Perfusion de 150 mg sur 2 h. Donne-moi le Cmax et l'AUC(0-t). |
| ood-008 | compare_pair | not_applicable | none_available | - | Perfusion de 150 mg sur 2 h. Donne-moi le Cmax et l'AUC(0-t). |
| ood-009 | asked_c0 | false | true | - | Et la MRT ? |
| ood-009 | asked_cl | false | true | - | Et la MRT ? |
| ood-009 | asked_half_life | false | true | - | Et la MRT ? |
| ood-009 | asked_lambda_z | false | true | - | Et la MRT ? |
| ood-009 | asked_tlag | false | true | - | Et la MRT ? |
| ood-009 | asked_vz | false | true | - | Et la MRT ? |
| ood-009 | auc_method | linear | not_applicable | - | Et la MRT ? |
| ood-010 | auc_method | linear | not_applicable | - | Perfusion de 500 µg pendant 1,5 h, Cmax et AUC0-inf. |
| ood-010 | compare_pair | not_applicable | none_available | - | Perfusion de 500 µg pendant 1,5 h, Cmax et AUC0-inf. |
| ood-011 | auc_method | linear | not_applicable | - | Perfusion de 500 µg pendant 90 minutes : que vaut l'AUC(0-t) ? |
| ood-011 | compare_pair | not_applicable | none_available | - | Perfusion de 500 µg pendant 90 minutes : que vaut l'AUC(0-t) ? |
| ood-012 | auc_method | linear | not_applicable | - | J'ai avalé 800 µg, les temps sont en minutes ; Cmax et AUC0-t. |
| ood-012 | compare_pair | not_applicable | none_available | - | J'ai avalé 800 µg, les temps sont en minutes ; Cmax et AUC0-t. |
| ood-013 | asked_auclast | true | false | - | Compare l'AUC linéaire et la lin-up/log-down. |
| ood-014 | asked_auclast | true | false | - | Compare les deux AUC (valeur et %). |
| ood-014 | auc_method | linear | not_applicable | - | Compare les deux AUC (valeur et %). |
| ood-015 | analysis | compare | none_needed | - | Compare l'analyse 2 à l'analyse 1. |
| ood-015 | auc_method | lin_up_log_down | not_applicable | - | Compare l'analyse 2 à l'analyse 1. |
| ood-015 | compare_pair | 2+3 | not_applicable | - | Compare l'analyse 2 à l'analyse 1. |
| ood-016 | auc_method | linear | not_applicable | - | Voie orale, 300 mg : y a-t-il un Tlag ? |
| ood-016 | compare_pair | not_applicable | none_available | - | Voie orale, 300 mg : y a-t-il un Tlag ? |
| ood-017 | analysis | none_needed | nca | - | Quel est le Tlag de ce bolus de 200 mg ? |
| ood-017 | asked_lambda_z | false | true | - | Quel est le Tlag de ce bolus de 200 mg ? |
| ood-017 | auc_method | linear | not_applicable | - | Quel est le Tlag de ce bolus de 200 mg ? |
| ood-017 | compare_pair | not_applicable | none_available | - | Quel est le Tlag de ce bolus de 200 mg ? |
| ood-017 | is_not_available | true | false | - | Quel est le Tlag de ce bolus de 200 mg ? |
| ood-018 | analysis | none_needed | nca | - | Quelle est la C0 après cette prise orale de 400 mg ? |
| ood-018 | auc_method | linear | not_applicable | - | Quelle est la C0 après cette prise orale de 400 mg ? |
| ood-018 | compare_pair | not_applicable | none_available | - | Quelle est la C0 après cette prise orale de 400 mg ? |
| ood-018 | is_not_available | true | false | - | Quelle est la C0 après cette prise orale de 400 mg ? |
| ood-019 | analysis | none_needed | nca | - | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-019 | compare_pair | not_applicable | none_available | - | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-019 | is_not_available | true | false | - | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-019 | route | oral | unknown | - | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-020 | analysis | none_needed | fit_pk2 | - | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. |
| ood-020 | compare_pair | not_applicable | none_available | - | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. |
| ood-020 | is_not_available | true | false | - | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. |
| ood-020 | route | oral | unknown | - | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. |
| ood-021 | asked_lambda_z | false | true | - | Après une prise orale, voici mes concentrations : quelle est la demi-vie ? |
| ood-021 | auc_method | linear | not_applicable | - | Après une prise orale, voici mes concentrations : quelle est la demi-vie ? |
| ood-021 | compare_pair | not_applicable | none_available | - | Après une prise orale, voici mes concentrations : quelle est la demi-vie ? |
| ood-022 | auc_method | linear | not_applicable | - | Prise orale de 100, voici les données. Cmax ? |
| ood-022 | compare_pair | not_applicable | none_available | - | Prise orale de 100, voici les données. Cmax ? |
| ood-023 | auc_method | linear | not_applicable | - | Bolus IV de 2 mg : donne-moi la clairance et le Vz. |
| ood-024 | auc_method | linear | not_applicable | - | Bolus de 2000 mcg : CL et Vz. |
| ood-024 | compare_pair | not_applicable | none_available | - | Bolus de 2000 mcg : CL et Vz. |
| ood-024 | dose_has_unit | false | true | - | Bolus de 2000 mcg : CL et Vz. |
| ood-025 | asked_aucinf | false | true | - | Et le pourcentage d'AUC extrapolée ? |
| ood-025 | auc_method | linear | not_applicable | - | Et le pourcentage d'AUC extrapolée ? |
| ood-026 | auc_method | linear | not_applicable | - | Il y a un zéro sous la LLOQ dans le tableau, on le garde ? Donne l'AUC(0-t) et la Cmax, dose orale 50 mg. |
| ood-026 | compare_pair | not_applicable | none_available | - | Il y a un zéro sous la LLOQ dans le tableau, on le garde ? Donne l'AUC(0-t) et la Cmax, dose orale 50 mg. |
| ood-027 | compare_pair | not_applicable | none_available | - | Simule les concentrations après une dose orale de 300 mg. |
| ood-028 | auc_method | linear | not_applicable | - | Donne-moi d'abord la demi-vie, ensuite la clairance et le Vz, pour cette dose orale de 300 mg. |
| ood-029 | compare_pair | not_applicable | none_available | - | Donne-moi le Cmax puis refais l'analyse en lin-up/log-down, bolus de 300 mg. |
| ood-030 | analysis | compare | nca | - | Refais l'analyse en lin-up/log-down et compare les deux AUC en valeur et en %. |
| ood-030 | asked_auclast | true | false | - | Refais l'analyse en lin-up/log-down et compare les deux AUC en valeur et en %. |
| ood-031 | auc_method | linear | not_applicable | - | Peux-tu me donner le Cmax, le Tmax et le t1/2 after a single oral dose of 100 mg ? |
| ood-032 | auc_method | linear | not_applicable | - | kel est le Cmax é le Tmax de ce tablo ? dose 400 mg per os |
| ood-033 | auc_method | linear | not_applicable | - | Dose orale de 500 mg : AUC0-∞ et AUC0-t. |
| ood-033 | compare_pair | not_applicable | none_available | - | Dose orale de 500 mg : AUC0-∞ et AUC0-t. |
| ood-034 | analysis | none_needed | nca | - | Bolus de 150 mg : quel est le Vdss ? |
| ood-034 | asked_vz | false | true | - | Bolus de 150 mg : quel est le Vdss ? |
| ood-034 | auc_method | linear | not_applicable | - | Bolus de 150 mg : quel est le Vdss ? |
| ood-034 | compare_pair | not_applicable | none_available | - | Bolus de 150 mg : quel est le Vdss ? |
| ood-034 | is_not_available | true | false | - | Bolus de 150 mg : quel est le Vdss ? |
| ood-035 | analysis | nca | fit_pk1 | - | Bolus de 150 mg : le R² ajusté et le nombre de points de la régression terminale. |
| ood-035 | auc_method | linear | not_applicable | - | Bolus de 150 mg : le R² ajusté et le nombre de points de la régression terminale. |
| ood-035 | compare_pair | not_applicable | none_available | - | Bolus de 150 mg : le R² ajusté et le nombre de points de la régression terminale. |
| ood-036 | asked_lambda_z | false | true | - | Prise unique de 100 mg par voie orale : je veux le MRT et la demi-vie. |
| ood-036 | auc_method | linear | not_applicable | - | Prise unique de 100 mg par voie orale : je veux le MRT et la demi-vie. |
| ood-036 | compare_pair | not_applicable | none_available | - | Prise unique de 100 mg par voie orale : je veux le MRT et la demi-vie. |
| ood-037 | auc_method | linear | not_applicable | - | Perfusion de 150 mg sur 2 h : clairance et volume de distribution. |
| ood-037 | compare_pair | not_applicable | none_available | - | Perfusion de 150 mg sur 2 h : clairance et volume de distribution. |
| ood-038 | analysis | none_needed | nca | - | Quel est le Tlag de cette perfusion de 150 mg ? |
| ood-038 | asked_lambda_z | false | true | - | Quel est le Tlag de cette perfusion de 150 mg ? |
| ood-038 | auc_method | linear | not_applicable | - | Quel est le Tlag de cette perfusion de 150 mg ? |
| ood-038 | compare_pair | not_applicable | none_available | - | Quel est le Tlag de cette perfusion de 150 mg ? |
| ood-038 | is_not_available | true | false | - | Quel est le Tlag de cette perfusion de 150 mg ? |
| ood-039 | auc_method | linear | not_applicable | - | Dose IV de 1000 µg : AUC(0-inf) et pourcentage extrapolé. |
| ood-039 | compare_pair | not_applicable | none_available | - | Dose IV de 1000 µg : AUC(0-inf) et pourcentage extrapolé. |
| ood-040 | analysis | nca | fit_pk1 | - | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? |
| ood-040 | asked_lambda_z | false | true | - | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? |
| ood-040 | auc_method | linear | not_applicable | - | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? |
| ood-040 | route | oral | unknown | - | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? |
| ood-041 | auc_method | linear | not_applicable | - | Bolus de 200 mg à t=0, temps en minutes : Cmax et Tmax. |
| ood-041 | compare_pair | not_applicable | none_available | - | Bolus de 200 mg à t=0, temps en minutes : Cmax et Tmax. |
| ood-042 | asked_lambda_z | false | true | - | Ajuste un bi-exponentiel sur ces données (bolus de 200 mg). |
| ood-042 | compare_pair | not_applicable | none_available | - | Ajuste un bi-exponentiel sur ces données (bolus de 200 mg). |
| ood-043 | auc_method | linear | not_applicable | - | Perfusion IV de 150 mg sur 2 h, CL et Vz svp. |
| ood-043 | compare_pair | not_applicable | none_available | - | Perfusion IV de 150 mg sur 2 h, CL et Vz svp. |
| ood-044 | auc_method | linear | not_applicable | - | Comprimé à libération prolongée de 5000 µg : Cmax, Tmax et demi-vie. |
| ood-044 | compare_pair | not_applicable | none_available | - | Comprimé à libération prolongée de 5000 µg : Cmax, Tmax et demi-vie. |
| ood-045 | auc_method | linear | not_applicable | - | Bolus de 300 mg, temps en minutes : AUC(0-t) et clairance. |
| ood-045 | compare_pair | not_applicable | none_available | - | Bolus de 300 mg, temps en minutes : AUC(0-t) et clairance. |
| ood-046 | auc_method | linear | not_applicable | - | Bolus de 150 mg : le Cl/F et le Vz/F ? |
| ood-046 | compare_pair | not_applicable | none_available | - | Bolus de 150 mg : le Cl/F et le Vz/F ? |
| ood-047 | analysis | nca | fit_pk1 | - | Voie orale, 100 mg : λz et t½. |
| ood-047 | auc_method | linear | not_applicable | - | Voie orale, 100 mg : λz et t½. |
| ood-047 | compare_pair | not_applicable | none_available | - | Voie orale, 100 mg : λz et t½. |
| ood-048 | analysis | none_needed | fit_pk1 | - | Voie orale, 300 mg : quelle est la constante d'absorption ka ? |
| ood-048 | auc_method | linear | not_applicable | - | Voie orale, 300 mg : quelle est la constante d'absorption ka ? |
| ood-048 | compare_pair | not_applicable | none_available | - | Voie orale, 300 mg : quelle est la constante d'absorption ka ? |
| ood-048 | is_not_available | true | false | - | Voie orale, 300 mg : quelle est la constante d'absorption ka ? |
| ood-049 | asked_tmax | false | true | - | Cmax et nombre de points de la régression terminale, dose orale de 100 mg. |
| ood-049 | auc_method | linear | not_applicable | - | Cmax et nombre de points de la régression terminale, dose orale de 100 mg. |
| ood-049 | compare_pair | not_applicable | none_available | - | Cmax et nombre de points de la régression terminale, dose orale de 100 mg. |
| ood-050 | compare_pair | not_applicable | none_available | - | AUC(0-t) par la méthode lin-up/log-down, dose orale de 50 mg. |
| ood-051 | auc_method | linear | not_applicable | - | Bolus de 2000 µg : l'AUC(0-t) tient-elle compte du point sous la LLOQ ? et le % extrapolé ? |
| ood-051 | compare_pair | not_applicable | none_available | - | Bolus de 2000 µg : l'AUC(0-t) tient-elle compte du point sous la LLOQ ? et le % extrapolé ? |
| ood-052 | compare_pair | not_applicable | none_available | - | Dose orale de 500 mg, méthode des trapèzes linéaires : AUC0-t. |
| ood-053 | auc_method | linear | not_applicable | - | Voici mes concentrations après 400 mg ; quel est le Cmax ? |
| ood-053 | compare_pair | not_applicable | none_available | - | Voici mes concentrations après 400 mg ; quel est le Cmax ? |
| ood-054 | auc_method | linear | not_applicable | - | Après une injection intraveineuse directe de 200 mg : C0 et Vz. |
| ood-054 | compare_pair | not_applicable | none_available | - | Après une injection intraveineuse directe de 200 mg : C0 et Vz. |
| ood-055 | auc_method | linear | not_applicable | - | Perfusion de 500 µg sur 90 min : Cmax. |
| ood-055 | compare_pair | not_applicable | none_available | - | Perfusion de 500 µg sur 90 min : Cmax. |
| ood-057 | asked_cmax | true | false | - | Compare le Cmax entre les deux méthodes. |
| ood-057 | auc_method | linear | not_applicable | - | Compare le Cmax entre les deux méthodes. |
| ood-058 | analysis | compare | nca | - | Compare les AUC linéaire et lin-up/log-down, dose orale de 400 mg. |
| ood-058 | asked_aucinf | false | true | - | Compare les AUC linéaire et lin-up/log-down, dose orale de 400 mg. |
| ood-058 | asked_auclast | true | false | - | Compare les AUC linéaire et lin-up/log-down, dose orale de 400 mg. |
| ood-058 | compare_pair | not_applicable | none_available | - | Compare les AUC linéaire et lin-up/log-down, dose orale de 400 mg. |
| ood-059 | auc_method | linear | not_applicable | - | 250 mg per os, voici les concentrations en µg/mL : Cmax, Tmax et AUC0-inf. |
| ood-059 | compare_pair | not_applicable | none_available | - | 250 mg per os, voici les concentrations en µg/mL : Cmax, Tmax et AUC0-inf. |
| ood-060 | analysis | none_needed | nca | - | Bolus IV de 120 mg : quel est le Tlag ? |
| ood-060 | asked_half_life | false | true | - | Bolus IV de 120 mg : quel est le Tlag ? |
| ood-060 | asked_lambda_z | false | true | - | Bolus IV de 120 mg : quel est le Tlag ? |
| ood-060 | auc_method | linear | not_applicable | - | Bolus IV de 120 mg : quel est le Tlag ? |
| ood-060 | compare_pair | not_applicable | none_available | - | Bolus IV de 120 mg : quel est le Tlag ? |
| ood-060 | is_not_available | true | false | - | Bolus IV de 120 mg : quel est le Tlag ? |
| ood-061 | analysis | none_needed | nca | - | Quelle est la C0 après cette prise orale de 200 mg ? |
| ood-061 | auc_method | linear | not_applicable | - | Quelle est la C0 après cette prise orale de 200 mg ? |
| ood-061 | compare_pair | not_applicable | none_available | - | Quelle est la C0 après cette prise orale de 200 mg ? |
| ood-061 | is_not_available | true | false | - | Quelle est la C0 après cette prise orale de 200 mg ? |
| ood-062 | auc_method | linear | not_applicable | - | Perfusion de 75 mg sur 1,5 h, les temps sont en minutes : Cmax. |
| ood-062 | compare_pair | not_applicable | none_available | - | Perfusion de 75 mg sur 1,5 h, les temps sont en minutes : Cmax. |
| ood-063 | asked_auclast | true | false | - | Étude à deux sujets, 300 mg par voie orale : Cmax et AUC0-t par sujet. |
| ood-063 | auc_method | linear | not_applicable | - | Étude à deux sujets, 300 mg par voie orale : Cmax et AUC0-t par sujet. |
| ood-063 | compare_pair | not_applicable | none_available | - | Étude à deux sujets, 300 mg par voie orale : Cmax et AUC0-t par sujet. |
| ood-064 | analysis | none_needed | nca | - | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-064 | asked_cmax | false | true | - | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-064 | compare_pair | not_applicable | none_available | - | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-064 | is_not_available | true | false | - | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-064 | route | oral | unknown | - | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-065 | analysis | none_needed | nca | - | Recueil urinaire : quantité excrétée et clairance rénale. |
| ood-065 | asked_cl | false | true | - | Recueil urinaire : quantité excrétée et clairance rénale. |
| ood-065 | compare_pair | not_applicable | none_available | - | Recueil urinaire : quantité excrétée et clairance rénale. |
| ood-066 | compare_pair | not_applicable | none_available | - | Ajuste un modèle à deux compartiments après 400 mg par voie orale. |
| ood-067 | asked_lambda_z | false | true | - | Voie orale 1200 mg, temps en minutes : t1/2 et MRT. |
| ood-067 | auc_method | linear | not_applicable | - | Voie orale 1200 mg, temps en minutes : t1/2 et MRT. |
| ood-067 | compare_pair | not_applicable | none_available | - | Voie orale 1200 mg, temps en minutes : t1/2 et MRT. |
| ood-068 | auc_method | linear | lin_up_log_down | - | 80 mg per os, il y a des zéros sous la LLOQ : AUC(0-t) et Cmax. |
| ood-068 | compare_pair | not_applicable | none_available | - | 80 mg per os, il y a des zéros sous la LLOQ : AUC(0-t) et Cmax. |
| ood-069 | asked_auclast | true | false | - | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. |
| ood-069 | auc_method | linear | not_applicable | - | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. |
| ood-069 | compare_pair | not_applicable | none_available | - | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. |
| ood-069 | dose_has_unit | false | true | - | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. |
| ood-070 | auc_method | linear | not_applicable | - | Perfusion de 750 µg sur 1 h : Vz et CL. |
| ood-070 | compare_pair | not_applicable | none_available | - | Perfusion de 750 µg sur 1 h : Vz et CL. |
| ood-071 | asked_auclast | true | false | - | Compare l'AUC linéaire et la lin-up/log-down. |
| ood-072 | analysis | compare | none_needed | - | Compare l'analyse 2 et l'analyse 1 pour l'AUC. |
| ood-072 | asked_auclast | true | false | - | Compare l'analyse 2 et l'analyse 1 pour l'AUC. |
| ood-072 | auc_method | lin_up_log_down | not_applicable | - | Compare l'analyse 2 et l'analyse 1 pour l'AUC. |
| ood-072 | compare_pair | 2+3 | not_applicable | - | Compare l'analyse 2 et l'analyse 1 pour l'AUC. |
| ood-073 | asked_auclast | true | false | - | Prise orale de 200 mg : Cmax, Tmax et AUC0-t. |
| ood-073 | auc_method | linear | not_applicable | - | Prise orale de 200 mg : Cmax, Tmax et AUC0-t. |
| ood-073 | compare_pair | not_applicable | none_available | - | Prise orale de 200 mg : Cmax, Tmax et AUC0-t. |
| ood-074 | auc_method | linear | not_applicable | - | Bolus de 120 mg : Cmax et AUC0-inf. |
| ood-074 | compare_pair | not_applicable | none_available | - | Bolus de 120 mg : Cmax et AUC0-inf. |
