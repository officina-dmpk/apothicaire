# Out-of-distribution requests: decider `rules-reviewer`, 2026-10-10

`decision/eval_ood.py`; 74 requests converted from `decision/ood/requests.jsonl` (schema report: `decision/ood/schema_report.md`).

## Scoring on the rows

74 rows, 1480 decisions: **89.9 %** correct overall; 1 of 74 rows have all their decisions right (1.4 %). Always-majority on these rows: 86.6 %; majority learned on train.jsonl: 81.4 %.

### Accuracy per question

| question | correct | total | accuracy | always-majority (these rows) | majority (train.jsonl) |
|---|---|---|---|---|---|
| analysis | 57 | 74 | 77.0 % | 60.8 % | 21.6 % |
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
| auc_method | 55 | 74 | 74.3 % | 77.0 % | 12.2 % |
| compare_pair | 74 | 74 | 100.0 % | 94.6 % | 94.6 % |
| dose_has_unit | 74 | 74 | 100.0 % | 93.2 % | 93.2 % |
| is_not_available | 68 | 74 | 91.9 % | 85.1 % | 85.1 % |
| route | 65 | 74 | 87.8 % | 54.1 % | 54.1 % |
| **overall** | 1330 | 1480 | **89.9 %** | 86.6 % | 81.4 % |

### Confusions (wrong cells only: gold -> predicted, count)

- `analysis`: none_needed -> nca (11); fit_pk2 -> nca (3); compare -> nca (1); fit_pk1 -> nca (1); simulate -> nca (1).
- `route`: oral -> unknown (7); iv_bolus -> unknown (2).
- `auc_method`: not_applicable -> linear (9); linear -> not_applicable (5); lin_up_log_down -> linear (3); linear -> lin_up_log_down (2).
- `compare_pair`: no error.
- `is_not_available`: true -> false (6).
- `dose_has_unit`: no error.
- `asked_<parameter>` (14 questions): 99 parameters asked and missed (of 99 asked), 0 parameters predicted asked that were not.

### Accuracy per tag (which kinds of hard requests break)

| tag | rows | decisions correct | accuracy | rows all right |
|---|---|---|---|---|
| abbreviation | 17 | 306/340 | 90.0 % | 0.0 % |
| bioequivalence | 1 | 16/20 | 80.0 % | 0.0 % |
| blq | 4 | 72/80 | 90.0 % | 0.0 % |
| c0 | 1 | 17/20 | 85.0 % | 0.0 % |
| colloquial | 6 | 108/120 | 90.0 % | 0.0 % |
| dose-unit-g | 1 | 18/20 | 90.0 % | 0.0 % |
| dose-unit-mcg | 1 | 18/20 | 90.0 % | 0.0 % |
| dose-unit-mg | 1 | 18/20 | 90.0 % | 0.0 % |
| dose-unit-micro | 9 | 160/180 | 88.9 % | 0.0 % |
| dose-without-unit | 1 | 19/20 | 95.0 % | 0.0 % |
| duration-unit-mismatch | 2 | 37/40 | 92.5 % | 0.0 % |
| duration-word | 1 | 19/20 | 95.0 % | 0.0 % |
| english-term | 1 | 19/20 | 95.0 % | 0.0 % |
| fit | 4 | 72/80 | 90.0 % | 0.0 % |
| follow-up | 4 | 71/80 | 88.8 % | 0.0 % |
| infusion | 7 | 128/140 | 91.4 % | 0.0 % |
| invented | 16 | 286/320 | 89.4 % | 0.0 % |
| iv-explicit | 1 | 18/20 | 90.0 % | 0.0 % |
| language-mix | 2 | 35/40 | 87.5 % | 0.0 % |
| latin-route | 3 | 53/60 | 88.3 % | 0.0 % |
| method-explicit | 2 | 37/40 | 92.5 % | 0.0 % |
| multi-subject | 1 | 18/20 | 90.0 % | 0.0 % |
| multiple-dose | 1 | 16/20 | 80.0 % | 0.0 % |
| no-dose | 1 | 19/20 | 95.0 % | 0.0 % |
| no-prior-analysis | 1 | 17/20 | 85.0 % | 0.0 % |
| non-auc-parameter | 1 | 18/20 | 90.0 % | 0.0 % |
| oral | 1 | 18/20 | 90.0 % | 0.0 % |
| out-of-scope | 4 | 65/80 | 81.2 % | 0.0 % |
| parameter-not-for-route | 5 | 90/100 | 90.0 % | 0.0 % |
| parameter-not-in-schema | 2 | 36/40 | 90.0 % | 0.0 % |
| plain | 2 | 35/40 | 87.5 % | 0.0 % |
| population | 1 | 16/20 | 80.0 % | 0.0 % |
| recall | 1 | 19/20 | 95.0 % | 0.0 % |
| rerun | 4 | 75/80 | 93.8 % | 0.0 % |
| route-implied | 5 | 86/100 | 86.0 % | 0.0 % |
| route-missing | 1 | 19/20 | 95.0 % | 0.0 % |
| route-stated | 8 | 145/160 | 90.6 % | 0.0 % |
| simulate | 1 | 18/20 | 90.0 % | 0.0 % |
| steady-state | 1 | 16/20 | 80.0 % | 0.0 % |
| terminology-mismatch | 2 | 37/40 | 92.5 % | 0.0 % |
| tlag | 1 | 19/20 | 95.0 % | 0.0 % |
| two-compartments | 2 | 36/40 | 90.0 % | 0.0 % |
| two-requests-in-one-sentence | 2 | 35/40 | 87.5 % | 0.0 % |
| typo | 2 | 36/40 | 90.0 % | 0.0 % |
| unicode | 1 | 18/20 | 90.0 % | 0.0 % |
| unit-conversion-in-text | 1 | 18/20 | 90.0 % | 0.0 % |
| unit-in-text | 5 | 90/100 | 90.0 % | 0.0 % |
| unit-variety | 1 | 17/20 | 85.0 % | 0.0 % |
| unrecognized-unit | 1 | 18/20 | 90.0 % | 0.0 % |
| urine | 1 | 17/20 | 85.0 % | 0.0 % |
| compare | 8 | 149/160 | 93.1 % | 12.5 % |
| by-id | 2 | 39/40 | 97.5 % | 50.0 % |
| no-parameter | 1 | 20/20 | 100.0 % | 100.0 % |

Tags that broke (share of fully correct rows below the overall share): abbreviation, bioequivalence, blq, c0, colloquial, dose-unit-g, dose-unit-mcg, dose-unit-mg, dose-unit-micro, dose-without-unit, duration-unit-mismatch, duration-word, english-term, fit, follow-up, infusion, invented, iv-explicit, language-mix, latin-route, method-explicit, multi-subject, multiple-dose, no-dose, no-prior-analysis, non-auc-parameter, oral, out-of-scope, parameter-not-for-route, parameter-not-in-schema, plain, population, recall, rerun, route-implied, route-missing, route-stated, simulate, steady-state, terminology-mismatch, tlag, two-compartments, two-requests-in-one-sentence, typo, unicode, unit-conversion-in-text, unit-in-text, unit-variety, unrecognized-unit, urine.

### Calibration (probability of the chosen label vs observed accuracy)

The decider gives labels without probabilities: no calibration table.

### Wrong decisions (150)

| row | question | gold | predicted | confidence | request |
|---|---|---|---|---|---|
| ood-001 | asked_cmax | true | false | - | J'ai pris un comprimé de 400 mg ce matin, voici mes concentrations. C'est quoi le Cmax et le Tmax ? |
| ood-001 | asked_tmax | true | false | - | J'ai pris un comprimé de 400 mg ce matin, voici mes concentrations. C'est quoi le Cmax et le Tmax ? |
| ood-001 | route | oral | unknown | - | J'ai pris un comprimé de 400 mg ce matin, voici mes concentrations. C'est quoi le Cmax et le Tmax ? |
| ood-002 | asked_half_life | true | false | - | et la t1/2 stp ? |
| ood-002 | auc_method | linear | not_applicable | - | et la t1/2 stp ? |
| ood-003 | asked_aucinf | true | false | - | AUC0-t et AUC0-inf svp |
| ood-003 | asked_auclast | true | false | - | AUC0-t et AUC0-inf svp |
| ood-003 | auc_method | linear | not_applicable | - | AUC0-t et AUC0-inf svp |
| ood-004 | asked_vz | true | false | - | bolus IV de 200 mg ; quel est le Vd ? |
| ood-005 | asked_cl | true | false | - | bolus de 200 mg : Cl/F ? |
| ood-006 | analysis | fit_pk2 | nca | - | Ajuste un modèle à deux compartiments après un bolus IV de 300 mg. |
| ood-006 | auc_method | not_applicable | linear | - | Ajuste un modèle à deux compartiments après un bolus IV de 300 mg. |
| ood-007 | analysis | fit_pk1 | nca | - | fit un modèle mono-compartiment sur ces données (bolus de 300 mg) |
| ood-007 | auc_method | not_applicable | linear | - | fit un modèle mono-compartiment sur ces données (bolus de 300 mg) |
| ood-008 | asked_auclast | true | false | - | Perfusion de 150 mg sur 2 h. Donne-moi le Cmax et l'AUC(0-t). |
| ood-008 | asked_cmax | true | false | - | Perfusion de 150 mg sur 2 h. Donne-moi le Cmax et l'AUC(0-t). |
| ood-009 | asked_mrt | true | false | - | Et la MRT ? |
| ood-009 | auc_method | linear | not_applicable | - | Et la MRT ? |
| ood-010 | asked_aucinf | true | false | - | Perfusion de 500 µg pendant 1,5 h, Cmax et AUC0-inf. |
| ood-010 | asked_cmax | true | false | - | Perfusion de 500 µg pendant 1,5 h, Cmax et AUC0-inf. |
| ood-011 | asked_auclast | true | false | - | Perfusion de 500 µg pendant 90 minutes : que vaut l'AUC(0-t) ? |
| ood-012 | asked_auclast | true | false | - | J'ai avalé 800 µg, les temps sont en minutes ; Cmax et AUC0-t. |
| ood-012 | asked_cmax | true | false | - | J'ai avalé 800 µg, les temps sont en minutes ; Cmax et AUC0-t. |
| ood-012 | route | oral | unknown | - | J'ai avalé 800 µg, les temps sont en minutes ; Cmax et AUC0-t. |
| ood-013 | asked_auclast | true | false | - | Compare l'AUC linéaire et la lin-up/log-down. |
| ood-014 | asked_auclast | true | false | - | Compare les deux AUC (valeur et %). |
| ood-014 | auc_method | linear | lin_up_log_down | - | Compare les deux AUC (valeur et %). |
| ood-016 | asked_tlag | true | false | - | Voie orale, 300 mg : y a-t-il un Tlag ? |
| ood-017 | analysis | none_needed | nca | - | Quel est le Tlag de ce bolus de 200 mg ? |
| ood-017 | asked_tlag | true | false | - | Quel est le Tlag de ce bolus de 200 mg ? |
| ood-018 | analysis | none_needed | nca | - | Quelle est la C0 après cette prise orale de 400 mg ? |
| ood-018 | asked_c0 | true | false | - | Quelle est la C0 après cette prise orale de 400 mg ? |
| ood-019 | analysis | none_needed | nca | - | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-019 | auc_method | not_applicable | linear | - | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-019 | is_not_available | true | false | - | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-019 | route | oral | unknown | - | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-020 | analysis | none_needed | nca | - | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. |
| ood-020 | auc_method | not_applicable | linear | - | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. |
| ood-020 | is_not_available | true | false | - | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. |
| ood-020 | route | oral | unknown | - | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. |
| ood-021 | asked_half_life | true | false | - | Après une prise orale, voici mes concentrations : quelle est la demi-vie ? |
| ood-022 | asked_cmax | true | false | - | Prise orale de 100, voici les données. Cmax ? |
| ood-023 | asked_cl | true | false | - | Bolus IV de 2 mg : donne-moi la clairance et le Vz. |
| ood-023 | asked_vz | true | false | - | Bolus IV de 2 mg : donne-moi la clairance et le Vz. |
| ood-024 | asked_cl | true | false | - | Bolus de 2000 mcg : CL et Vz. |
| ood-024 | asked_vz | true | false | - | Bolus de 2000 mcg : CL et Vz. |
| ood-025 | asked_aucpext | true | false | - | Et le pourcentage d'AUC extrapolée ? |
| ood-025 | auc_method | linear | not_applicable | - | Et le pourcentage d'AUC extrapolée ? |
| ood-026 | asked_auclast | true | false | - | Il y a un zéro sous la LLOQ dans le tableau, on le garde ? Donne l'AUC(0-t) et la Cmax, dose orale 50 mg. |
| ood-026 | asked_cmax | true | false | - | Il y a un zéro sous la LLOQ dans le tableau, on le garde ? Donne l'AUC(0-t) et la Cmax, dose orale 50 mg. |
| ood-027 | analysis | simulate | nca | - | Simule les concentrations après une dose orale de 300 mg. |
| ood-027 | auc_method | not_applicable | linear | - | Simule les concentrations après une dose orale de 300 mg. |
| ood-028 | asked_cl | true | false | - | Donne-moi d'abord la demi-vie, ensuite la clairance et le Vz, pour cette dose orale de 300 mg. |
| ood-028 | asked_half_life | true | false | - | Donne-moi d'abord la demi-vie, ensuite la clairance et le Vz, pour cette dose orale de 300 mg. |
| ood-028 | asked_vz | true | false | - | Donne-moi d'abord la demi-vie, ensuite la clairance et le Vz, pour cette dose orale de 300 mg. |
| ood-029 | asked_cmax | true | false | - | Donne-moi le Cmax puis refais l'analyse en lin-up/log-down, bolus de 300 mg. |
| ood-029 | auc_method | lin_up_log_down | linear | - | Donne-moi le Cmax puis refais l'analyse en lin-up/log-down, bolus de 300 mg. |
| ood-030 | asked_auclast | true | false | - | Refais l'analyse en lin-up/log-down et compare les deux AUC en valeur et en %. |
| ood-031 | asked_cmax | true | false | - | Peux-tu me donner le Cmax, le Tmax et le t1/2 after a single oral dose of 100 mg ? |
| ood-031 | asked_half_life | true | false | - | Peux-tu me donner le Cmax, le Tmax et le t1/2 after a single oral dose of 100 mg ? |
| ood-031 | asked_tmax | true | false | - | Peux-tu me donner le Cmax, le Tmax et le t1/2 after a single oral dose of 100 mg ? |
| ood-032 | asked_cmax | true | false | - | kel est le Cmax é le Tmax de ce tablo ? dose 400 mg per os |
| ood-032 | asked_tmax | true | false | - | kel est le Cmax é le Tmax de ce tablo ? dose 400 mg per os |
| ood-033 | asked_aucinf | true | false | - | Dose orale de 500 mg : AUC0-∞ et AUC0-t. |
| ood-033 | asked_auclast | true | false | - | Dose orale de 500 mg : AUC0-∞ et AUC0-t. |
| ood-034 | analysis | none_needed | nca | - | Bolus de 150 mg : quel est le Vdss ? |
| ood-034 | is_not_available | true | false | - | Bolus de 150 mg : quel est le Vdss ? |
| ood-035 | asked_adj_r2 | true | false | - | Bolus de 150 mg : le R² ajusté et le nombre de points de la régression terminale. |
| ood-035 | asked_lambda_z_points | true | false | - | Bolus de 150 mg : le R² ajusté et le nombre de points de la régression terminale. |
| ood-036 | asked_half_life | true | false | - | Prise unique de 100 mg par voie orale : je veux le MRT et la demi-vie. |
| ood-036 | asked_mrt | true | false | - | Prise unique de 100 mg par voie orale : je veux le MRT et la demi-vie. |
| ood-037 | asked_cl | true | false | - | Perfusion de 150 mg sur 2 h : clairance et volume de distribution. |
| ood-037 | asked_vz | true | false | - | Perfusion de 150 mg sur 2 h : clairance et volume de distribution. |
| ood-038 | analysis | none_needed | nca | - | Quel est le Tlag de cette perfusion de 150 mg ? |
| ood-038 | asked_tlag | true | false | - | Quel est le Tlag de cette perfusion de 150 mg ? |
| ood-039 | asked_aucinf | true | false | - | Dose IV de 1000 µg : AUC(0-inf) et pourcentage extrapolé. |
| ood-039 | asked_aucpext | true | false | - | Dose IV de 1000 µg : AUC(0-inf) et pourcentage extrapolé. |
| ood-039 | route | iv_bolus | unknown | - | Dose IV de 1000 µg : AUC(0-inf) et pourcentage extrapolé. |
| ood-040 | asked_half_life | true | false | - | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? |
| ood-040 | route | oral | unknown | - | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? |
| ood-041 | asked_cmax | true | false | - | Bolus de 200 mg à t=0, temps en minutes : Cmax et Tmax. |
| ood-041 | asked_tmax | true | false | - | Bolus de 200 mg à t=0, temps en minutes : Cmax et Tmax. |
| ood-042 | analysis | fit_pk2 | nca | - | Ajuste un bi-exponentiel sur ces données (bolus de 200 mg). |
| ood-042 | auc_method | not_applicable | linear | - | Ajuste un bi-exponentiel sur ces données (bolus de 200 mg). |
| ood-043 | asked_cl | true | false | - | Perfusion IV de 150 mg sur 2 h, CL et Vz svp. |
| ood-043 | asked_vz | true | false | - | Perfusion IV de 150 mg sur 2 h, CL et Vz svp. |
| ood-044 | asked_cmax | true | false | - | Comprimé à libération prolongée de 5000 µg : Cmax, Tmax et demi-vie. |
| ood-044 | asked_half_life | true | false | - | Comprimé à libération prolongée de 5000 µg : Cmax, Tmax et demi-vie. |
| ood-044 | asked_tmax | true | false | - | Comprimé à libération prolongée de 5000 µg : Cmax, Tmax et demi-vie. |
| ood-044 | route | oral | unknown | - | Comprimé à libération prolongée de 5000 µg : Cmax, Tmax et demi-vie. |
| ood-045 | asked_auclast | true | false | - | Bolus de 300 mg, temps en minutes : AUC(0-t) et clairance. |
| ood-045 | asked_cl | true | false | - | Bolus de 300 mg, temps en minutes : AUC(0-t) et clairance. |
| ood-046 | asked_cl | true | false | - | Bolus de 150 mg : le Cl/F et le Vz/F ? |
| ood-046 | asked_vz | true | false | - | Bolus de 150 mg : le Cl/F et le Vz/F ? |
| ood-047 | asked_half_life | true | false | - | Voie orale, 100 mg : λz et t½. |
| ood-047 | asked_lambda_z | true | false | - | Voie orale, 100 mg : λz et t½. |
| ood-048 | analysis | none_needed | nca | - | Voie orale, 300 mg : quelle est la constante d'absorption ka ? |
| ood-048 | is_not_available | true | false | - | Voie orale, 300 mg : quelle est la constante d'absorption ka ? |
| ood-049 | asked_cmax | true | false | - | Cmax et nombre de points de la régression terminale, dose orale de 100 mg. |
| ood-049 | asked_lambda_z_points | true | false | - | Cmax et nombre de points de la régression terminale, dose orale de 100 mg. |
| ood-050 | asked_auclast | true | false | - | AUC(0-t) par la méthode lin-up/log-down, dose orale de 50 mg. |
| ood-050 | auc_method | lin_up_log_down | linear | - | AUC(0-t) par la méthode lin-up/log-down, dose orale de 50 mg. |
| ood-051 | asked_auclast | true | false | - | Bolus de 2000 µg : l'AUC(0-t) tient-elle compte du point sous la LLOQ ? et le % extrapolé ? |
| ood-051 | asked_aucpext | true | false | - | Bolus de 2000 µg : l'AUC(0-t) tient-elle compte du point sous la LLOQ ? et le % extrapolé ? |
| ood-052 | asked_auclast | true | false | - | Dose orale de 500 mg, méthode des trapèzes linéaires : AUC0-t. |
| ood-053 | asked_cmax | true | false | - | Voici mes concentrations après 400 mg ; quel est le Cmax ? |
| ood-054 | asked_c0 | true | false | - | Après une injection intraveineuse directe de 200 mg : C0 et Vz. |
| ood-054 | asked_vz | true | false | - | Après une injection intraveineuse directe de 200 mg : C0 et Vz. |
| ood-054 | route | iv_bolus | unknown | - | Après une injection intraveineuse directe de 200 mg : C0 et Vz. |
| ood-055 | asked_cmax | true | false | - | Perfusion de 500 µg sur 90 min : Cmax. |
| ood-056 | auc_method | linear | not_applicable | - | Rappelle-moi la dose et la méthode d'AUC utilisées. |
| ood-057 | asked_cmax | true | false | - | Compare le Cmax entre les deux méthodes. |
| ood-057 | auc_method | linear | lin_up_log_down | - | Compare le Cmax entre les deux méthodes. |
| ood-058 | analysis | compare | nca | - | Compare les AUC linéaire et lin-up/log-down, dose orale de 400 mg. |
| ood-058 | asked_auclast | true | false | - | Compare les AUC linéaire et lin-up/log-down, dose orale de 400 mg. |
| ood-058 | auc_method | lin_up_log_down | linear | - | Compare les AUC linéaire et lin-up/log-down, dose orale de 400 mg. |
| ood-059 | asked_aucinf | true | false | - | 250 mg per os, voici les concentrations en µg/mL : Cmax, Tmax et AUC0-inf. |
| ood-059 | asked_cmax | true | false | - | 250 mg per os, voici les concentrations en µg/mL : Cmax, Tmax et AUC0-inf. |
| ood-059 | asked_tmax | true | false | - | 250 mg per os, voici les concentrations en µg/mL : Cmax, Tmax et AUC0-inf. |
| ood-060 | analysis | none_needed | nca | - | Bolus IV de 120 mg : quel est le Tlag ? |
| ood-060 | asked_tlag | true | false | - | Bolus IV de 120 mg : quel est le Tlag ? |
| ood-061 | analysis | none_needed | nca | - | Quelle est la C0 après cette prise orale de 200 mg ? |
| ood-061 | asked_c0 | true | false | - | Quelle est la C0 après cette prise orale de 200 mg ? |
| ood-062 | asked_cmax | true | false | - | Perfusion de 75 mg sur 1,5 h, les temps sont en minutes : Cmax. |
| ood-063 | asked_auclast | true | false | - | Étude à deux sujets, 300 mg par voie orale : Cmax et AUC0-t par sujet. |
| ood-063 | asked_cmax | true | false | - | Étude à deux sujets, 300 mg par voie orale : Cmax et AUC0-t par sujet. |
| ood-064 | analysis | none_needed | nca | - | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-064 | auc_method | not_applicable | linear | - | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-064 | is_not_available | true | false | - | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-064 | route | oral | unknown | - | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-065 | analysis | none_needed | nca | - | Recueil urinaire : quantité excrétée et clairance rénale. |
| ood-065 | auc_method | not_applicable | linear | - | Recueil urinaire : quantité excrétée et clairance rénale. |
| ood-065 | is_not_available | true | false | - | Recueil urinaire : quantité excrétée et clairance rénale. |
| ood-066 | analysis | fit_pk2 | nca | - | Ajuste un modèle à deux compartiments après 400 mg par voie orale. |
| ood-066 | auc_method | not_applicable | linear | - | Ajuste un modèle à deux compartiments après 400 mg par voie orale. |
| ood-067 | asked_half_life | true | false | - | Voie orale 1200 mg, temps en minutes : t1/2 et MRT. |
| ood-067 | asked_mrt | true | false | - | Voie orale 1200 mg, temps en minutes : t1/2 et MRT. |
| ood-068 | asked_auclast | true | false | - | 80 mg per os, il y a des zéros sous la LLOQ : AUC(0-t) et Cmax. |
| ood-068 | asked_cmax | true | false | - | 80 mg per os, il y a des zéros sous la LLOQ : AUC(0-t) et Cmax. |
| ood-069 | asked_auclast | true | false | - | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. |
| ood-069 | asked_cmax | true | false | - | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. |
| ood-070 | asked_cl | true | false | - | Perfusion de 750 µg sur 1 h : Vz et CL. |
| ood-070 | asked_vz | true | false | - | Perfusion de 750 µg sur 1 h : Vz et CL. |
| ood-071 | asked_auclast | true | false | - | Compare l'AUC linéaire et la lin-up/log-down. |
| ood-072 | asked_auclast | true | false | - | Compare l'analyse 2 et l'analyse 1 pour l'AUC. |
| ood-073 | asked_auclast | true | false | - | Prise orale de 200 mg : Cmax, Tmax et AUC0-t. |
| ood-073 | asked_cmax | true | false | - | Prise orale de 200 mg : Cmax, Tmax et AUC0-t. |
| ood-073 | asked_tmax | true | false | - | Prise orale de 200 mg : Cmax, Tmax et AUC0-t. |
| ood-074 | asked_aucinf | true | false | - | Bolus de 120 mg : Cmax et AUC0-inf. |
| ood-074 | asked_cmax | true | false | - | Bolus de 120 mg : Cmax et AUC0-inf. |
