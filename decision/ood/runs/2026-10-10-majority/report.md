# Out-of-distribution requests: decider `majority`, 2026-10-10

`decision/eval_ood.py`; 74 requests converted from `decision/ood/requests.jsonl` (schema report: `decision/ood/schema_report.md`).

## Scoring on the rows

74 rows, 1480 decisions: **81.4 %** correct overall; 0 of 74 rows have all their decisions right (0.0 %). Always-majority on these rows: 86.6 %; majority learned on train.jsonl: 81.4 %.

### Accuracy per question

| question | correct | total | accuracy | always-majority (these rows) | majority (train.jsonl) |
|---|---|---|---|---|---|
| analysis | 16 | 74 | 21.6 % | 60.8 % | 21.6 % |
| asked_adj_r2 | 73 | 74 | 98.6 % | 98.6 % | 98.6 % |
| asked_aucinf | 68 | 74 | 91.9 % | 91.9 % | 91.9 % |
| asked_auclast | 54 | 74 | 73.0 % | 73.0 % | 73.0 % |
| asked_aucpext | 71 | 74 | 95.9 % | 95.9 % | 95.9 % |
| asked_c0 | 71 | 74 | 95.9 % | 95.9 % | 95.9 % |
| asked_cl | 65 | 74 | 87.8 % | 87.8 % | 87.8 % |
| asked_cmax | 52 | 74 | 70.3 % | 70.3 % | 70.3 % |
| asked_half_life | 65 | 74 | 87.8 % | 87.8 % | 87.8 % |
| asked_lambda_z | 73 | 74 | 98.6 % | 98.6 % | 98.6 % |
| asked_lambda_z_points | 72 | 74 | 97.3 % | 97.3 % | 97.3 % |
| asked_mrt | 71 | 74 | 95.9 % | 95.9 % | 95.9 % |
| asked_tlag | 70 | 74 | 94.6 % | 94.6 % | 94.6 % |
| asked_tmax | 67 | 74 | 90.5 % | 90.5 % | 90.5 % |
| asked_vz | 65 | 74 | 87.8 % | 87.8 % | 87.8 % |
| auc_method | 9 | 74 | 12.2 % | 77.0 % | 12.2 % |
| compare_pair | 70 | 74 | 94.6 % | 94.6 % | 94.6 % |
| dose_has_unit | 69 | 74 | 93.2 % | 93.2 % | 93.2 % |
| is_not_available | 63 | 74 | 85.1 % | 85.1 % | 85.1 % |
| route | 40 | 74 | 54.1 % | 54.1 % | 54.1 % |
| **overall** | 1204 | 1480 | **81.4 %** | 86.6 % | 81.4 % |

### Confusions (wrong cells only: gold -> predicted, count)

- `analysis`: nca -> none_needed (45); compare -> none_needed (8); fit_pk2 -> none_needed (3); fit_pk1 -> none_needed (1); simulate -> none_needed (1).
- `route`: iv_bolus -> oral (22); iv_infusion -> oral (10); unknown -> oral (2).
- `auc_method`: linear -> not_applicable (57); lin_up_log_down -> not_applicable (8).
- `compare_pair`: 2+3 -> not_applicable (4).
- `is_not_available`: true -> false (11).
- `dose_has_unit`: false -> true (5).
- `asked_<parameter>` (14 questions): 99 parameters asked and missed (of 99 asked), 0 parameters predicted asked that were not.

### Accuracy per tag (which kinds of hard requests break)

| tag | rows | decisions correct | accuracy | rows all right |
|---|---|---|---|---|
| abbreviation | 17 | 275/340 | 80.9 % | 0.0 % |
| bioequivalence | 1 | 19/20 | 95.0 % | 0.0 % |
| blq | 4 | 64/80 | 80.0 % | 0.0 % |
| by-id | 2 | 33/40 | 82.5 % | 0.0 % |
| c0 | 1 | 15/20 | 75.0 % | 0.0 % |
| colloquial | 6 | 96/120 | 80.0 % | 0.0 % |
| compare | 8 | 131/160 | 81.9 % | 0.0 % |
| dose-unit-g | 1 | 15/20 | 75.0 % | 0.0 % |
| dose-unit-mcg | 1 | 14/20 | 70.0 % | 0.0 % |
| dose-unit-mg | 1 | 15/20 | 75.0 % | 0.0 % |
| dose-unit-micro | 9 | 140/180 | 77.8 % | 0.0 % |
| dose-without-unit | 1 | 16/20 | 80.0 % | 0.0 % |
| duration-unit-mismatch | 2 | 31/40 | 77.5 % | 0.0 % |
| duration-word | 1 | 16/20 | 80.0 % | 0.0 % |
| english-term | 1 | 17/20 | 85.0 % | 0.0 % |
| fit | 4 | 73/80 | 91.2 % | 0.0 % |
| follow-up | 4 | 69/80 | 86.2 % | 0.0 % |
| infusion | 7 | 108/140 | 77.1 % | 0.0 % |
| invented | 16 | 260/320 | 81.2 % | 0.0 % |
| iv-explicit | 1 | 16/20 | 80.0 % | 0.0 % |
| language-mix | 2 | 33/40 | 82.5 % | 0.0 % |
| latin-route | 3 | 47/60 | 78.3 % | 0.0 % |
| method-explicit | 2 | 34/40 | 85.0 % | 0.0 % |
| multi-subject | 1 | 16/20 | 80.0 % | 0.0 % |
| multiple-dose | 1 | 19/20 | 95.0 % | 0.0 % |
| no-dose | 1 | 16/20 | 80.0 % | 0.0 % |
| no-parameter | 1 | 17/20 | 85.0 % | 0.0 % |
| no-prior-analysis | 1 | 17/20 | 85.0 % | 0.0 % |
| non-auc-parameter | 1 | 15/20 | 75.0 % | 0.0 % |
| oral | 1 | 19/20 | 95.0 % | 0.0 % |
| out-of-scope | 4 | 74/80 | 92.5 % | 0.0 % |
| parameter-not-for-route | 5 | 82/100 | 82.0 % | 0.0 % |
| parameter-not-in-schema | 2 | 35/40 | 87.5 % | 0.0 % |
| plain | 2 | 30/40 | 75.0 % | 0.0 % |
| population | 1 | 19/20 | 95.0 % | 0.0 % |
| recall | 1 | 19/20 | 95.0 % | 0.0 % |
| rerun | 4 | 66/80 | 82.5 % | 0.0 % |
| route-implied | 5 | 78/100 | 78.0 % | 0.0 % |
| route-missing | 1 | 16/20 | 80.0 % | 0.0 % |
| route-stated | 8 | 124/160 | 77.5 % | 0.0 % |
| simulate | 1 | 19/20 | 95.0 % | 0.0 % |
| steady-state | 1 | 19/20 | 95.0 % | 0.0 % |
| terminology-mismatch | 2 | 31/40 | 77.5 % | 0.0 % |
| tlag | 1 | 17/20 | 85.0 % | 0.0 % |
| two-compartments | 2 | 36/40 | 90.0 % | 0.0 % |
| two-requests-in-one-sentence | 2 | 31/40 | 77.5 % | 0.0 % |
| typo | 2 | 34/40 | 85.0 % | 0.0 % |
| unicode | 1 | 16/20 | 80.0 % | 0.0 % |
| unit-conversion-in-text | 1 | 15/20 | 75.0 % | 0.0 % |
| unit-in-text | 5 | 76/100 | 76.0 % | 0.0 % |
| unit-variety | 1 | 15/20 | 75.0 % | 0.0 % |
| unrecognized-unit | 1 | 14/20 | 70.0 % | 0.0 % |
| urine | 1 | 17/20 | 85.0 % | 0.0 % |

Tags that broke (share of fully correct rows below the overall share): none.

### Calibration (probability of the chosen label vs observed accuracy)

The decider gives labels without probabilities: no calibration table.

### Wrong decisions (276)

| row | question | gold | predicted | confidence | request |
|---|---|---|---|---|---|
| ood-001 | analysis | nca | none_needed | - | J'ai pris un comprimé de 400 mg ce matin, voici mes concentrations. C'est quoi le Cmax et le Tmax ? |
| ood-001 | asked_cmax | true | false | - | J'ai pris un comprimé de 400 mg ce matin, voici mes concentrations. C'est quoi le Cmax et le Tmax ? |
| ood-001 | asked_tmax | true | false | - | J'ai pris un comprimé de 400 mg ce matin, voici mes concentrations. C'est quoi le Cmax et le Tmax ? |
| ood-001 | auc_method | linear | not_applicable | - | J'ai pris un comprimé de 400 mg ce matin, voici mes concentrations. C'est quoi le Cmax et le Tmax ? |
| ood-002 | asked_half_life | true | false | - | et la t1/2 stp ? |
| ood-002 | auc_method | linear | not_applicable | - | et la t1/2 stp ? |
| ood-003 | asked_aucinf | true | false | - | AUC0-t et AUC0-inf svp |
| ood-003 | asked_auclast | true | false | - | AUC0-t et AUC0-inf svp |
| ood-003 | auc_method | linear | not_applicable | - | AUC0-t et AUC0-inf svp |
| ood-004 | analysis | nca | none_needed | - | bolus IV de 200 mg ; quel est le Vd ? |
| ood-004 | asked_vz | true | false | - | bolus IV de 200 mg ; quel est le Vd ? |
| ood-004 | auc_method | linear | not_applicable | - | bolus IV de 200 mg ; quel est le Vd ? |
| ood-004 | route | iv_bolus | oral | - | bolus IV de 200 mg ; quel est le Vd ? |
| ood-005 | analysis | nca | none_needed | - | bolus de 200 mg : Cl/F ? |
| ood-005 | asked_cl | true | false | - | bolus de 200 mg : Cl/F ? |
| ood-005 | auc_method | linear | not_applicable | - | bolus de 200 mg : Cl/F ? |
| ood-005 | route | iv_bolus | oral | - | bolus de 200 mg : Cl/F ? |
| ood-006 | analysis | fit_pk2 | none_needed | - | Ajuste un modèle à deux compartiments après un bolus IV de 300 mg. |
| ood-006 | route | iv_bolus | oral | - | Ajuste un modèle à deux compartiments après un bolus IV de 300 mg. |
| ood-007 | analysis | fit_pk1 | none_needed | - | fit un modèle mono-compartiment sur ces données (bolus de 300 mg) |
| ood-007 | route | iv_bolus | oral | - | fit un modèle mono-compartiment sur ces données (bolus de 300 mg) |
| ood-008 | analysis | nca | none_needed | - | Perfusion de 150 mg sur 2 h. Donne-moi le Cmax et l'AUC(0-t). |
| ood-008 | asked_auclast | true | false | - | Perfusion de 150 mg sur 2 h. Donne-moi le Cmax et l'AUC(0-t). |
| ood-008 | asked_cmax | true | false | - | Perfusion de 150 mg sur 2 h. Donne-moi le Cmax et l'AUC(0-t). |
| ood-008 | auc_method | linear | not_applicable | - | Perfusion de 150 mg sur 2 h. Donne-moi le Cmax et l'AUC(0-t). |
| ood-008 | route | iv_infusion | oral | - | Perfusion de 150 mg sur 2 h. Donne-moi le Cmax et l'AUC(0-t). |
| ood-009 | asked_mrt | true | false | - | Et la MRT ? |
| ood-009 | auc_method | linear | not_applicable | - | Et la MRT ? |
| ood-009 | route | iv_infusion | oral | - | Et la MRT ? |
| ood-010 | analysis | nca | none_needed | - | Perfusion de 500 µg pendant 1,5 h, Cmax et AUC0-inf. |
| ood-010 | asked_aucinf | true | false | - | Perfusion de 500 µg pendant 1,5 h, Cmax et AUC0-inf. |
| ood-010 | asked_cmax | true | false | - | Perfusion de 500 µg pendant 1,5 h, Cmax et AUC0-inf. |
| ood-010 | auc_method | linear | not_applicable | - | Perfusion de 500 µg pendant 1,5 h, Cmax et AUC0-inf. |
| ood-010 | route | iv_infusion | oral | - | Perfusion de 500 µg pendant 1,5 h, Cmax et AUC0-inf. |
| ood-011 | analysis | nca | none_needed | - | Perfusion de 500 µg pendant 90 minutes : que vaut l'AUC(0-t) ? |
| ood-011 | asked_auclast | true | false | - | Perfusion de 500 µg pendant 90 minutes : que vaut l'AUC(0-t) ? |
| ood-011 | auc_method | linear | not_applicable | - | Perfusion de 500 µg pendant 90 minutes : que vaut l'AUC(0-t) ? |
| ood-011 | route | iv_infusion | oral | - | Perfusion de 500 µg pendant 90 minutes : que vaut l'AUC(0-t) ? |
| ood-012 | analysis | nca | none_needed | - | J'ai avalé 800 µg, les temps sont en minutes ; Cmax et AUC0-t. |
| ood-012 | asked_auclast | true | false | - | J'ai avalé 800 µg, les temps sont en minutes ; Cmax et AUC0-t. |
| ood-012 | asked_cmax | true | false | - | J'ai avalé 800 µg, les temps sont en minutes ; Cmax et AUC0-t. |
| ood-012 | auc_method | linear | not_applicable | - | J'ai avalé 800 µg, les temps sont en minutes ; Cmax et AUC0-t. |
| ood-013 | analysis | compare | none_needed | - | Compare l'AUC linéaire et la lin-up/log-down. |
| ood-013 | asked_auclast | true | false | - | Compare l'AUC linéaire et la lin-up/log-down. |
| ood-013 | auc_method | lin_up_log_down | not_applicable | - | Compare l'AUC linéaire et la lin-up/log-down. |
| ood-014 | analysis | compare | none_needed | - | Compare les deux AUC (valeur et %). |
| ood-014 | asked_auclast | true | false | - | Compare les deux AUC (valeur et %). |
| ood-014 | auc_method | linear | not_applicable | - | Compare les deux AUC (valeur et %). |
| ood-014 | compare_pair | 2+3 | not_applicable | - | Compare les deux AUC (valeur et %). |
| ood-015 | analysis | compare | none_needed | - | Compare l'analyse 2 à l'analyse 1. |
| ood-015 | auc_method | lin_up_log_down | not_applicable | - | Compare l'analyse 2 à l'analyse 1. |
| ood-015 | compare_pair | 2+3 | not_applicable | - | Compare l'analyse 2 à l'analyse 1. |
| ood-016 | analysis | nca | none_needed | - | Voie orale, 300 mg : y a-t-il un Tlag ? |
| ood-016 | asked_tlag | true | false | - | Voie orale, 300 mg : y a-t-il un Tlag ? |
| ood-016 | auc_method | linear | not_applicable | - | Voie orale, 300 mg : y a-t-il un Tlag ? |
| ood-017 | asked_tlag | true | false | - | Quel est le Tlag de ce bolus de 200 mg ? |
| ood-017 | auc_method | linear | not_applicable | - | Quel est le Tlag de ce bolus de 200 mg ? |
| ood-017 | is_not_available | true | false | - | Quel est le Tlag de ce bolus de 200 mg ? |
| ood-017 | route | iv_bolus | oral | - | Quel est le Tlag de ce bolus de 200 mg ? |
| ood-018 | asked_c0 | true | false | - | Quelle est la C0 après cette prise orale de 400 mg ? |
| ood-018 | auc_method | linear | not_applicable | - | Quelle est la C0 après cette prise orale de 400 mg ? |
| ood-018 | is_not_available | true | false | - | Quelle est la C0 après cette prise orale de 400 mg ? |
| ood-019 | is_not_available | true | false | - | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-020 | is_not_available | true | false | - | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. |
| ood-021 | analysis | nca | none_needed | - | Après une prise orale, voici mes concentrations : quelle est la demi-vie ? |
| ood-021 | asked_half_life | true | false | - | Après une prise orale, voici mes concentrations : quelle est la demi-vie ? |
| ood-021 | auc_method | linear | not_applicable | - | Après une prise orale, voici mes concentrations : quelle est la demi-vie ? |
| ood-021 | dose_has_unit | false | true | - | Après une prise orale, voici mes concentrations : quelle est la demi-vie ? |
| ood-022 | analysis | nca | none_needed | - | Prise orale de 100, voici les données. Cmax ? |
| ood-022 | asked_cmax | true | false | - | Prise orale de 100, voici les données. Cmax ? |
| ood-022 | auc_method | linear | not_applicable | - | Prise orale de 100, voici les données. Cmax ? |
| ood-022 | dose_has_unit | false | true | - | Prise orale de 100, voici les données. Cmax ? |
| ood-023 | analysis | nca | none_needed | - | Bolus IV de 2 mg : donne-moi la clairance et le Vz. |
| ood-023 | asked_cl | true | false | - | Bolus IV de 2 mg : donne-moi la clairance et le Vz. |
| ood-023 | asked_vz | true | false | - | Bolus IV de 2 mg : donne-moi la clairance et le Vz. |
| ood-023 | auc_method | linear | not_applicable | - | Bolus IV de 2 mg : donne-moi la clairance et le Vz. |
| ood-023 | route | iv_bolus | oral | - | Bolus IV de 2 mg : donne-moi la clairance et le Vz. |
| ood-024 | analysis | nca | none_needed | - | Bolus de 2000 mcg : CL et Vz. |
| ood-024 | asked_cl | true | false | - | Bolus de 2000 mcg : CL et Vz. |
| ood-024 | asked_vz | true | false | - | Bolus de 2000 mcg : CL et Vz. |
| ood-024 | auc_method | linear | not_applicable | - | Bolus de 2000 mcg : CL et Vz. |
| ood-024 | dose_has_unit | false | true | - | Bolus de 2000 mcg : CL et Vz. |
| ood-024 | route | iv_bolus | oral | - | Bolus de 2000 mcg : CL et Vz. |
| ood-025 | asked_aucpext | true | false | - | Et le pourcentage d'AUC extrapolée ? |
| ood-025 | auc_method | linear | not_applicable | - | Et le pourcentage d'AUC extrapolée ? |
| ood-025 | route | iv_bolus | oral | - | Et le pourcentage d'AUC extrapolée ? |
| ood-026 | analysis | nca | none_needed | - | Il y a un zéro sous la LLOQ dans le tableau, on le garde ? Donne l'AUC(0-t) et la Cmax, dose orale 50 mg. |
| ood-026 | asked_auclast | true | false | - | Il y a un zéro sous la LLOQ dans le tableau, on le garde ? Donne l'AUC(0-t) et la Cmax, dose orale 50 mg. |
| ood-026 | asked_cmax | true | false | - | Il y a un zéro sous la LLOQ dans le tableau, on le garde ? Donne l'AUC(0-t) et la Cmax, dose orale 50 mg. |
| ood-026 | auc_method | linear | not_applicable | - | Il y a un zéro sous la LLOQ dans le tableau, on le garde ? Donne l'AUC(0-t) et la Cmax, dose orale 50 mg. |
| ood-027 | analysis | simulate | none_needed | - | Simule les concentrations après une dose orale de 300 mg. |
| ood-028 | analysis | nca | none_needed | - | Donne-moi d'abord la demi-vie, ensuite la clairance et le Vz, pour cette dose orale de 300 mg. |
| ood-028 | asked_cl | true | false | - | Donne-moi d'abord la demi-vie, ensuite la clairance et le Vz, pour cette dose orale de 300 mg. |
| ood-028 | asked_half_life | true | false | - | Donne-moi d'abord la demi-vie, ensuite la clairance et le Vz, pour cette dose orale de 300 mg. |
| ood-028 | asked_vz | true | false | - | Donne-moi d'abord la demi-vie, ensuite la clairance et le Vz, pour cette dose orale de 300 mg. |
| ood-028 | auc_method | linear | not_applicable | - | Donne-moi d'abord la demi-vie, ensuite la clairance et le Vz, pour cette dose orale de 300 mg. |
| ood-029 | analysis | nca | none_needed | - | Donne-moi le Cmax puis refais l'analyse en lin-up/log-down, bolus de 300 mg. |
| ood-029 | asked_cmax | true | false | - | Donne-moi le Cmax puis refais l'analyse en lin-up/log-down, bolus de 300 mg. |
| ood-029 | auc_method | lin_up_log_down | not_applicable | - | Donne-moi le Cmax puis refais l'analyse en lin-up/log-down, bolus de 300 mg. |
| ood-029 | route | iv_bolus | oral | - | Donne-moi le Cmax puis refais l'analyse en lin-up/log-down, bolus de 300 mg. |
| ood-030 | analysis | compare | none_needed | - | Refais l'analyse en lin-up/log-down et compare les deux AUC en valeur et en %. |
| ood-030 | asked_auclast | true | false | - | Refais l'analyse en lin-up/log-down et compare les deux AUC en valeur et en %. |
| ood-030 | auc_method | lin_up_log_down | not_applicable | - | Refais l'analyse en lin-up/log-down et compare les deux AUC en valeur et en %. |
| ood-030 | route | iv_bolus | oral | - | Refais l'analyse en lin-up/log-down et compare les deux AUC en valeur et en %. |
| ood-031 | analysis | nca | none_needed | - | Peux-tu me donner le Cmax, le Tmax et le t1/2 after a single oral dose of 100 mg ? |
| ood-031 | asked_cmax | true | false | - | Peux-tu me donner le Cmax, le Tmax et le t1/2 after a single oral dose of 100 mg ? |
| ood-031 | asked_half_life | true | false | - | Peux-tu me donner le Cmax, le Tmax et le t1/2 after a single oral dose of 100 mg ? |
| ood-031 | asked_tmax | true | false | - | Peux-tu me donner le Cmax, le Tmax et le t1/2 after a single oral dose of 100 mg ? |
| ood-031 | auc_method | linear | not_applicable | - | Peux-tu me donner le Cmax, le Tmax et le t1/2 after a single oral dose of 100 mg ? |
| ood-032 | analysis | nca | none_needed | - | kel est le Cmax é le Tmax de ce tablo ? dose 400 mg per os |
| ood-032 | asked_cmax | true | false | - | kel est le Cmax é le Tmax de ce tablo ? dose 400 mg per os |
| ood-032 | asked_tmax | true | false | - | kel est le Cmax é le Tmax de ce tablo ? dose 400 mg per os |
| ood-032 | auc_method | linear | not_applicable | - | kel est le Cmax é le Tmax de ce tablo ? dose 400 mg per os |
| ood-033 | analysis | nca | none_needed | - | Dose orale de 500 mg : AUC0-∞ et AUC0-t. |
| ood-033 | asked_aucinf | true | false | - | Dose orale de 500 mg : AUC0-∞ et AUC0-t. |
| ood-033 | asked_auclast | true | false | - | Dose orale de 500 mg : AUC0-∞ et AUC0-t. |
| ood-033 | auc_method | linear | not_applicable | - | Dose orale de 500 mg : AUC0-∞ et AUC0-t. |
| ood-034 | auc_method | linear | not_applicable | - | Bolus de 150 mg : quel est le Vdss ? |
| ood-034 | is_not_available | true | false | - | Bolus de 150 mg : quel est le Vdss ? |
| ood-034 | route | iv_bolus | oral | - | Bolus de 150 mg : quel est le Vdss ? |
| ood-035 | analysis | nca | none_needed | - | Bolus de 150 mg : le R² ajusté et le nombre de points de la régression terminale. |
| ood-035 | asked_adj_r2 | true | false | - | Bolus de 150 mg : le R² ajusté et le nombre de points de la régression terminale. |
| ood-035 | asked_lambda_z_points | true | false | - | Bolus de 150 mg : le R² ajusté et le nombre de points de la régression terminale. |
| ood-035 | auc_method | linear | not_applicable | - | Bolus de 150 mg : le R² ajusté et le nombre de points de la régression terminale. |
| ood-035 | route | iv_bolus | oral | - | Bolus de 150 mg : le R² ajusté et le nombre de points de la régression terminale. |
| ood-036 | analysis | nca | none_needed | - | Prise unique de 100 mg par voie orale : je veux le MRT et la demi-vie. |
| ood-036 | asked_half_life | true | false | - | Prise unique de 100 mg par voie orale : je veux le MRT et la demi-vie. |
| ood-036 | asked_mrt | true | false | - | Prise unique de 100 mg par voie orale : je veux le MRT et la demi-vie. |
| ood-036 | auc_method | linear | not_applicable | - | Prise unique de 100 mg par voie orale : je veux le MRT et la demi-vie. |
| ood-037 | analysis | nca | none_needed | - | Perfusion de 150 mg sur 2 h : clairance et volume de distribution. |
| ood-037 | asked_cl | true | false | - | Perfusion de 150 mg sur 2 h : clairance et volume de distribution. |
| ood-037 | asked_vz | true | false | - | Perfusion de 150 mg sur 2 h : clairance et volume de distribution. |
| ood-037 | auc_method | linear | not_applicable | - | Perfusion de 150 mg sur 2 h : clairance et volume de distribution. |
| ood-037 | route | iv_infusion | oral | - | Perfusion de 150 mg sur 2 h : clairance et volume de distribution. |
| ood-038 | asked_tlag | true | false | - | Quel est le Tlag de cette perfusion de 150 mg ? |
| ood-038 | auc_method | linear | not_applicable | - | Quel est le Tlag de cette perfusion de 150 mg ? |
| ood-038 | is_not_available | true | false | - | Quel est le Tlag de cette perfusion de 150 mg ? |
| ood-038 | route | iv_infusion | oral | - | Quel est le Tlag de cette perfusion de 150 mg ? |
| ood-039 | analysis | nca | none_needed | - | Dose IV de 1000 µg : AUC(0-inf) et pourcentage extrapolé. |
| ood-039 | asked_aucinf | true | false | - | Dose IV de 1000 µg : AUC(0-inf) et pourcentage extrapolé. |
| ood-039 | asked_aucpext | true | false | - | Dose IV de 1000 µg : AUC(0-inf) et pourcentage extrapolé. |
| ood-039 | auc_method | linear | not_applicable | - | Dose IV de 1000 µg : AUC(0-inf) et pourcentage extrapolé. |
| ood-039 | route | iv_bolus | oral | - | Dose IV de 1000 µg : AUC(0-inf) et pourcentage extrapolé. |
| ood-040 | analysis | nca | none_needed | - | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? |
| ood-040 | asked_half_life | true | false | - | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? |
| ood-040 | auc_method | linear | not_applicable | - | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? |
| ood-041 | analysis | nca | none_needed | - | Bolus de 200 mg à t=0, temps en minutes : Cmax et Tmax. |
| ood-041 | asked_cmax | true | false | - | Bolus de 200 mg à t=0, temps en minutes : Cmax et Tmax. |
| ood-041 | asked_tmax | true | false | - | Bolus de 200 mg à t=0, temps en minutes : Cmax et Tmax. |
| ood-041 | auc_method | linear | not_applicable | - | Bolus de 200 mg à t=0, temps en minutes : Cmax et Tmax. |
| ood-041 | route | iv_bolus | oral | - | Bolus de 200 mg à t=0, temps en minutes : Cmax et Tmax. |
| ood-042 | analysis | fit_pk2 | none_needed | - | Ajuste un bi-exponentiel sur ces données (bolus de 200 mg). |
| ood-042 | route | iv_bolus | oral | - | Ajuste un bi-exponentiel sur ces données (bolus de 200 mg). |
| ood-043 | analysis | nca | none_needed | - | Perfusion IV de 150 mg sur 2 h, CL et Vz svp. |
| ood-043 | asked_cl | true | false | - | Perfusion IV de 150 mg sur 2 h, CL et Vz svp. |
| ood-043 | asked_vz | true | false | - | Perfusion IV de 150 mg sur 2 h, CL et Vz svp. |
| ood-043 | auc_method | linear | not_applicable | - | Perfusion IV de 150 mg sur 2 h, CL et Vz svp. |
| ood-043 | route | iv_infusion | oral | - | Perfusion IV de 150 mg sur 2 h, CL et Vz svp. |
| ood-044 | analysis | nca | none_needed | - | Comprimé à libération prolongée de 5000 µg : Cmax, Tmax et demi-vie. |
| ood-044 | asked_cmax | true | false | - | Comprimé à libération prolongée de 5000 µg : Cmax, Tmax et demi-vie. |
| ood-044 | asked_half_life | true | false | - | Comprimé à libération prolongée de 5000 µg : Cmax, Tmax et demi-vie. |
| ood-044 | asked_tmax | true | false | - | Comprimé à libération prolongée de 5000 µg : Cmax, Tmax et demi-vie. |
| ood-044 | auc_method | linear | not_applicable | - | Comprimé à libération prolongée de 5000 µg : Cmax, Tmax et demi-vie. |
| ood-045 | analysis | nca | none_needed | - | Bolus de 300 mg, temps en minutes : AUC(0-t) et clairance. |
| ood-045 | asked_auclast | true | false | - | Bolus de 300 mg, temps en minutes : AUC(0-t) et clairance. |
| ood-045 | asked_cl | true | false | - | Bolus de 300 mg, temps en minutes : AUC(0-t) et clairance. |
| ood-045 | auc_method | linear | not_applicable | - | Bolus de 300 mg, temps en minutes : AUC(0-t) et clairance. |
| ood-045 | route | iv_bolus | oral | - | Bolus de 300 mg, temps en minutes : AUC(0-t) et clairance. |
| ood-046 | analysis | nca | none_needed | - | Bolus de 150 mg : le Cl/F et le Vz/F ? |
| ood-046 | asked_cl | true | false | - | Bolus de 150 mg : le Cl/F et le Vz/F ? |
| ood-046 | asked_vz | true | false | - | Bolus de 150 mg : le Cl/F et le Vz/F ? |
| ood-046 | auc_method | linear | not_applicable | - | Bolus de 150 mg : le Cl/F et le Vz/F ? |
| ood-046 | route | iv_bolus | oral | - | Bolus de 150 mg : le Cl/F et le Vz/F ? |
| ood-047 | analysis | nca | none_needed | - | Voie orale, 100 mg : λz et t½. |
| ood-047 | asked_half_life | true | false | - | Voie orale, 100 mg : λz et t½. |
| ood-047 | asked_lambda_z | true | false | - | Voie orale, 100 mg : λz et t½. |
| ood-047 | auc_method | linear | not_applicable | - | Voie orale, 100 mg : λz et t½. |
| ood-048 | auc_method | linear | not_applicable | - | Voie orale, 300 mg : quelle est la constante d'absorption ka ? |
| ood-048 | is_not_available | true | false | - | Voie orale, 300 mg : quelle est la constante d'absorption ka ? |
| ood-049 | analysis | nca | none_needed | - | Cmax et nombre de points de la régression terminale, dose orale de 100 mg. |
| ood-049 | asked_cmax | true | false | - | Cmax et nombre de points de la régression terminale, dose orale de 100 mg. |
| ood-049 | asked_lambda_z_points | true | false | - | Cmax et nombre de points de la régression terminale, dose orale de 100 mg. |
| ood-049 | auc_method | linear | not_applicable | - | Cmax et nombre de points de la régression terminale, dose orale de 100 mg. |
| ood-050 | analysis | nca | none_needed | - | AUC(0-t) par la méthode lin-up/log-down, dose orale de 50 mg. |
| ood-050 | asked_auclast | true | false | - | AUC(0-t) par la méthode lin-up/log-down, dose orale de 50 mg. |
| ood-050 | auc_method | lin_up_log_down | not_applicable | - | AUC(0-t) par la méthode lin-up/log-down, dose orale de 50 mg. |
| ood-051 | analysis | nca | none_needed | - | Bolus de 2000 µg : l'AUC(0-t) tient-elle compte du point sous la LLOQ ? et le % extrapolé ? |
| ood-051 | asked_auclast | true | false | - | Bolus de 2000 µg : l'AUC(0-t) tient-elle compte du point sous la LLOQ ? et le % extrapolé ? |
| ood-051 | asked_aucpext | true | false | - | Bolus de 2000 µg : l'AUC(0-t) tient-elle compte du point sous la LLOQ ? et le % extrapolé ? |
| ood-051 | auc_method | linear | not_applicable | - | Bolus de 2000 µg : l'AUC(0-t) tient-elle compte du point sous la LLOQ ? et le % extrapolé ? |
| ood-051 | route | iv_bolus | oral | - | Bolus de 2000 µg : l'AUC(0-t) tient-elle compte du point sous la LLOQ ? et le % extrapolé ? |
| ood-052 | analysis | nca | none_needed | - | Dose orale de 500 mg, méthode des trapèzes linéaires : AUC0-t. |
| ood-052 | asked_auclast | true | false | - | Dose orale de 500 mg, méthode des trapèzes linéaires : AUC0-t. |
| ood-052 | auc_method | linear | not_applicable | - | Dose orale de 500 mg, méthode des trapèzes linéaires : AUC0-t. |
| ood-053 | analysis | nca | none_needed | - | Voici mes concentrations après 400 mg ; quel est le Cmax ? |
| ood-053 | asked_cmax | true | false | - | Voici mes concentrations après 400 mg ; quel est le Cmax ? |
| ood-053 | auc_method | linear | not_applicable | - | Voici mes concentrations après 400 mg ; quel est le Cmax ? |
| ood-053 | route | unknown | oral | - | Voici mes concentrations après 400 mg ; quel est le Cmax ? |
| ood-054 | analysis | nca | none_needed | - | Après une injection intraveineuse directe de 200 mg : C0 et Vz. |
| ood-054 | asked_c0 | true | false | - | Après une injection intraveineuse directe de 200 mg : C0 et Vz. |
| ood-054 | asked_vz | true | false | - | Après une injection intraveineuse directe de 200 mg : C0 et Vz. |
| ood-054 | auc_method | linear | not_applicable | - | Après une injection intraveineuse directe de 200 mg : C0 et Vz. |
| ood-054 | route | iv_bolus | oral | - | Après une injection intraveineuse directe de 200 mg : C0 et Vz. |
| ood-055 | analysis | nca | none_needed | - | Perfusion de 500 µg sur 90 min : Cmax. |
| ood-055 | asked_cmax | true | false | - | Perfusion de 500 µg sur 90 min : Cmax. |
| ood-055 | auc_method | linear | not_applicable | - | Perfusion de 500 µg sur 90 min : Cmax. |
| ood-055 | route | iv_infusion | oral | - | Perfusion de 500 µg sur 90 min : Cmax. |
| ood-056 | auc_method | linear | not_applicable | - | Rappelle-moi la dose et la méthode d'AUC utilisées. |
| ood-057 | analysis | compare | none_needed | - | Compare le Cmax entre les deux méthodes. |
| ood-057 | asked_cmax | true | false | - | Compare le Cmax entre les deux méthodes. |
| ood-057 | auc_method | linear | not_applicable | - | Compare le Cmax entre les deux méthodes. |
| ood-057 | compare_pair | 2+3 | not_applicable | - | Compare le Cmax entre les deux méthodes. |
| ood-057 | route | iv_bolus | oral | - | Compare le Cmax entre les deux méthodes. |
| ood-058 | analysis | compare | none_needed | - | Compare les AUC linéaire et lin-up/log-down, dose orale de 400 mg. |
| ood-058 | asked_auclast | true | false | - | Compare les AUC linéaire et lin-up/log-down, dose orale de 400 mg. |
| ood-058 | auc_method | lin_up_log_down | not_applicable | - | Compare les AUC linéaire et lin-up/log-down, dose orale de 400 mg. |
| ood-059 | analysis | nca | none_needed | - | 250 mg per os, voici les concentrations en µg/mL : Cmax, Tmax et AUC0-inf. |
| ood-059 | asked_aucinf | true | false | - | 250 mg per os, voici les concentrations en µg/mL : Cmax, Tmax et AUC0-inf. |
| ood-059 | asked_cmax | true | false | - | 250 mg per os, voici les concentrations en µg/mL : Cmax, Tmax et AUC0-inf. |
| ood-059 | asked_tmax | true | false | - | 250 mg per os, voici les concentrations en µg/mL : Cmax, Tmax et AUC0-inf. |
| ood-059 | auc_method | linear | not_applicable | - | 250 mg per os, voici les concentrations en µg/mL : Cmax, Tmax et AUC0-inf. |
| ood-060 | asked_tlag | true | false | - | Bolus IV de 120 mg : quel est le Tlag ? |
| ood-060 | auc_method | linear | not_applicable | - | Bolus IV de 120 mg : quel est le Tlag ? |
| ood-060 | is_not_available | true | false | - | Bolus IV de 120 mg : quel est le Tlag ? |
| ood-060 | route | iv_bolus | oral | - | Bolus IV de 120 mg : quel est le Tlag ? |
| ood-061 | asked_c0 | true | false | - | Quelle est la C0 après cette prise orale de 200 mg ? |
| ood-061 | auc_method | linear | not_applicable | - | Quelle est la C0 après cette prise orale de 200 mg ? |
| ood-061 | is_not_available | true | false | - | Quelle est la C0 après cette prise orale de 200 mg ? |
| ood-062 | analysis | nca | none_needed | - | Perfusion de 75 mg sur 1,5 h, les temps sont en minutes : Cmax. |
| ood-062 | asked_cmax | true | false | - | Perfusion de 75 mg sur 1,5 h, les temps sont en minutes : Cmax. |
| ood-062 | auc_method | linear | not_applicable | - | Perfusion de 75 mg sur 1,5 h, les temps sont en minutes : Cmax. |
| ood-062 | route | iv_infusion | oral | - | Perfusion de 75 mg sur 1,5 h, les temps sont en minutes : Cmax. |
| ood-063 | analysis | nca | none_needed | - | Étude à deux sujets, 300 mg par voie orale : Cmax et AUC0-t par sujet. |
| ood-063 | asked_auclast | true | false | - | Étude à deux sujets, 300 mg par voie orale : Cmax et AUC0-t par sujet. |
| ood-063 | asked_cmax | true | false | - | Étude à deux sujets, 300 mg par voie orale : Cmax et AUC0-t par sujet. |
| ood-063 | auc_method | linear | not_applicable | - | Étude à deux sujets, 300 mg par voie orale : Cmax et AUC0-t par sujet. |
| ood-064 | is_not_available | true | false | - | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-065 | dose_has_unit | false | true | - | Recueil urinaire : quantité excrétée et clairance rénale. |
| ood-065 | is_not_available | true | false | - | Recueil urinaire : quantité excrétée et clairance rénale. |
| ood-065 | route | unknown | oral | - | Recueil urinaire : quantité excrétée et clairance rénale. |
| ood-066 | analysis | fit_pk2 | none_needed | - | Ajuste un modèle à deux compartiments après 400 mg par voie orale. |
| ood-067 | analysis | nca | none_needed | - | Voie orale 1200 mg, temps en minutes : t1/2 et MRT. |
| ood-067 | asked_half_life | true | false | - | Voie orale 1200 mg, temps en minutes : t1/2 et MRT. |
| ood-067 | asked_mrt | true | false | - | Voie orale 1200 mg, temps en minutes : t1/2 et MRT. |
| ood-067 | auc_method | linear | not_applicable | - | Voie orale 1200 mg, temps en minutes : t1/2 et MRT. |
| ood-068 | analysis | nca | none_needed | - | 80 mg per os, il y a des zéros sous la LLOQ : AUC(0-t) et Cmax. |
| ood-068 | asked_auclast | true | false | - | 80 mg per os, il y a des zéros sous la LLOQ : AUC(0-t) et Cmax. |
| ood-068 | asked_cmax | true | false | - | 80 mg per os, il y a des zéros sous la LLOQ : AUC(0-t) et Cmax. |
| ood-068 | auc_method | linear | not_applicable | - | 80 mg per os, il y a des zéros sous la LLOQ : AUC(0-t) et Cmax. |
| ood-069 | analysis | nca | none_needed | - | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. |
| ood-069 | asked_auclast | true | false | - | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. |
| ood-069 | asked_cmax | true | false | - | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. |
| ood-069 | auc_method | linear | not_applicable | - | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. |
| ood-069 | dose_has_unit | false | true | - | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. |
| ood-070 | analysis | nca | none_needed | - | Perfusion de 750 µg sur 1 h : Vz et CL. |
| ood-070 | asked_cl | true | false | - | Perfusion de 750 µg sur 1 h : Vz et CL. |
| ood-070 | asked_vz | true | false | - | Perfusion de 750 µg sur 1 h : Vz et CL. |
| ood-070 | auc_method | linear | not_applicable | - | Perfusion de 750 µg sur 1 h : Vz et CL. |
| ood-070 | route | iv_infusion | oral | - | Perfusion de 750 µg sur 1 h : Vz et CL. |
| ood-071 | analysis | compare | none_needed | - | Compare l'AUC linéaire et la lin-up/log-down. |
| ood-071 | asked_auclast | true | false | - | Compare l'AUC linéaire et la lin-up/log-down. |
| ood-071 | auc_method | lin_up_log_down | not_applicable | - | Compare l'AUC linéaire et la lin-up/log-down. |
| ood-072 | analysis | compare | none_needed | - | Compare l'analyse 2 et l'analyse 1 pour l'AUC. |
| ood-072 | asked_auclast | true | false | - | Compare l'analyse 2 et l'analyse 1 pour l'AUC. |
| ood-072 | auc_method | lin_up_log_down | not_applicable | - | Compare l'analyse 2 et l'analyse 1 pour l'AUC. |
| ood-072 | compare_pair | 2+3 | not_applicable | - | Compare l'analyse 2 et l'analyse 1 pour l'AUC. |
| ood-073 | analysis | nca | none_needed | - | Prise orale de 200 mg : Cmax, Tmax et AUC0-t. |
| ood-073 | asked_auclast | true | false | - | Prise orale de 200 mg : Cmax, Tmax et AUC0-t. |
| ood-073 | asked_cmax | true | false | - | Prise orale de 200 mg : Cmax, Tmax et AUC0-t. |
| ood-073 | asked_tmax | true | false | - | Prise orale de 200 mg : Cmax, Tmax et AUC0-t. |
| ood-073 | auc_method | linear | not_applicable | - | Prise orale de 200 mg : Cmax, Tmax et AUC0-t. |
| ood-074 | analysis | nca | none_needed | - | Bolus de 120 mg : Cmax et AUC0-inf. |
| ood-074 | asked_aucinf | true | false | - | Bolus de 120 mg : Cmax et AUC0-inf. |
| ood-074 | asked_cmax | true | false | - | Bolus de 120 mg : Cmax et AUC0-inf. |
| ood-074 | auc_method | linear | not_applicable | - | Bolus de 120 mg : Cmax et AUC0-inf. |
| ood-074 | route | iv_bolus | oral | - | Bolus de 120 mg : Cmax et AUC0-inf. |
