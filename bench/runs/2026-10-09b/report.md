# Apothicaire benchmark report

date: 2026-10-09b, exercises_run: 25, model: Bonsai 2 27B (Ternary-Bonsai-2-27B-PTQ1_0), temperature 0.3, no fixed seed

**Hallucination rate = numbers not found in a tool result or user message / numbers checked (deterministic gate `gate.py`).**

- before the gate's regeneration (first drafts): **0 / 926 = 0.0 %** (none observed: upper 95 % bound by the rule of three 3/926 = 0.32 %)
- in the answers shown (gate in the loop): **0 / 926 = 0.0 %** (none observed: upper 95 % bound by the rule of three 3/926 = 0.32 %)
- 25 exercises, 200 turns (0 failed by an error); turns with an unverified number: 0 before, 0 after; regenerated 0 (regeneration kept 0); turns shown with the badge: 0

## Failure taxonomy (unverified numbers)

| class | before the gate | in the answers shown |
|---|---|---|
| unit_conversion | 0 | 0 |
| arithmetic | 0 | 0 |
| unlabelled_misread | 0 | 0 |
| recall_error | 0 | 0 |
| other | 0 | 0 |

Classes are heuristics (`bench/score.py`); the unverified counts above never depend on them. Chance baseline: how the same rules classify random numbers of 3 and 4 significant digits drawn over each exercise's range of tool values (a class whose baseline share is large is weak evidence at that precision):

| class | random 3-digit numbers | random 4-digit numbers |
|---|---|---|
| unit_conversion | 10.9 % | 3.8 % |
| arithmetic | 0.0 % | 22.2 % |
| unlabelled_misread | 11.8 % | 8.4 % |
| recall_error | 0.0 % | 0.0 % |
| other | 77.4 % | 65.6 % |

## Correctness: 195 / 200 turns fully correct; expected numbers found 552 / 556; forbidden (converted or computed) values present in 0 answers

| question type | turns | correct | found / expected numbers | unverified / total before | unverified / total shown |
|---|---|---|---|---|---|
| import_nca | 25 | 25 (100.0 %) | 225 / 225 | 0 / 421 | 0 / 421 |
| cmax_tmax | 25 | 25 (100.0 %) | 58 / 58 | 0 / 63 | 0 / 63 |
| clearance_volume | 25 | 25 (100.0 %) | 50 / 50 | 0 / 53 | 0 / 53 |
| half_life | 25 | 25 (100.0 %) | 50 / 50 | 0 / 137 | 0 / 137 |
| lambda_z_regression | 25 | 25 (100.0 %) | 50 / 50 | 0 / 80 | 0 / 80 |
| recall | 25 | 22 (88.0 %) | 25 / 25 | 0 / 28 | 0 / 28 |
| compare | 25 | 23 (92.0 %) | 94 / 98 | 0 / 141 | 0 / 141 |
| not_available | 25 | 25 (100.0 %) | 0 / 0 | 0 / 3 | 0 / 3 |

## Compare turn and `analysis_compare`: called in 25 of 25 compare turns (30 calls, 30 valid; 30 calls in all turns); usable in 24 (the two analyses of the exercise, the auclast row with difference and percentage, equal to the ground-truth arithmetic: then the engine's difference and percentage are expected and allowed, other computed values stay forbidden); row disagreeing with the ground truth: 0; no call: 0


## Oracle check: 170 / 175 turns = 97.1 % (95 % CI, exercises resampled: 94.9-99.4 %); 549 / 556 expected numbers = 98.7 % (95 % CI, exercises resampled: 97.6-99.6 %)

Second judgement, independent of the gate (`bench/score.py`, `oracle_turn`): the number written after the label of the parameter the question asks for must be Caladrius's value of THAT parameter, of the right AUC method, with the unit Caladrius reports. The gate counts above are untouched; the denominators here are the turns that expect numbers and the numbers they expect (not covered: not_available, no value to check).

| question type | turns | oracle-correct | expected numbers ok | wrong_parameter | wrong_method | wrong_option | missing_unit | wrong_unit | missing_value |
|---|---|---|---|---|---|---|---|---|---|
| import_nca | 25 | 25 (100.0 %) | 225 / 225 | 0 | 0 | 0 | 0 | 0 | 0 |
| cmax_tmax | 25 | 25 (100.0 %) | 58 / 58 | 0 | 0 | 0 | 0 | 0 | 0 |
| clearance_volume | 25 | 25 (100.0 %) | 50 / 50 | 0 | 0 | 0 | 0 | 0 | 0 |
| half_life | 25 | 25 (100.0 %) | 50 / 50 | 0 | 0 | 0 | 0 | 0 | 0 |
| lambda_z_regression | 25 | 25 (100.0 %) | 50 / 50 | 0 | 0 | 0 | 0 | 0 | 0 |
| recall | 25 | 22 (88.0 %) | 22 / 25 | 0 | 0 | 0 | 3 | 0 | 0 |
| compare | 25 | 23 (92.0 %) | 94 / 98 | 0 | 0 | 0 | 0 | 0 | 4 |
| **total** | 175 | 170 (97.1 %) | 549 / 556 | 0 | 0 | 0 | 3 | 0 | 4 |

Against the scorer's expected-number check (the global search of the numbers, above): items the scorer found but the oracle rejects 3 (ex17_oral_1 t6 dose (missing_unit); ex22_pk2_oral_1 t6 dose (missing_unit); ex25_oral_1 t6 dose (missing_unit)); items the scorer missed but the oracle accepts 0; turns oracle-wrong but scorer-correct 0; turns oracle-correct but scorer-incorrect 0.

Every expected number the oracle rejects:

| exercise | turn | expected | class | detail | numbers written after the label |
|---|---|---|---|---|---|
| ex12_iv_infusion | 7 compare | AUC(0-tlast) linear | missing_value |  | 3, 3 |
| ex12_iv_infusion | 7 compare | AUC(0-tlast) lin-up/log-down | missing_value |  | 3, 3 |
| ex17_oral_1 | 6 recall | dose | missing_unit |  | 500 |
| ex22_pk2_oral_1 | 6 recall | dose | missing_unit |  | 500 |
| ex23_iv_bolus | 7 compare | AUC(0-tlast) linear | missing_value |  | 2 min*ng/ml, 2 128 760,0 min*ng/ml |
| ex23_iv_bolus | 7 compare | AUC(0-tlast) lin-up/log-down | missing_value |  | 3, 3 min*ng/ml, 2 092 970,0 min*ng/ml, 35 789,1 min*ng/ml |
| ex25_oral_1 | 6 recall | dose | missing_unit |  | 100 |

## Tool calls: 160 valid, 0 invalid, 0 failed of 160 (validity 100.0 %)

`nca_run` calls: 52, with the right dose 52, with the right route 50; memory calls (zoom / read_message): 9; by tool: {'analysis_compare': 30, 'analysis_get': 52, 'data_import': 25, 'export_table': 1, 'nca_run': 52}. invalid = unknown tool, invalid_parameters, unknown_worksheet / unknown_analysis or any rejection; failed = accepted but the analysis errs for every subject.

## Tool-call argument audit: 2 of 77 `nca_run` / `data_import` calls differ from the exercise's intent (dose, route, AUC method alone as options; the CSV and the column units)

| deviation | calls |
|---|---|
| nca_run: route = "iv_bolus" (intended "extravascular") | 2 |

In exercises: ex04_oral_1_lag. A deviation is listed here whatever its effect; the oracle check calls it `wrong_option` only when the answer's value is wrong (`run_bench.py --tool-arg-audit` prints every call).

## Time: mean 10.4 s per turn, mean 4691 prompt tokens (first call), total 73 min

## Per exercise

| exercise | dose | units | unverified / total before | unverified / total shown | correct turns | badge turns | calls valid / total | mean s per turn |
|---|---|---|---|---|---|---|---|---|
| ex01_iv_bolus | 200 mg | h, mg/L | 0 / 44 | 0 / 44 | 8 / 8 | 0 | 5 / 5 | 9.4 |
| ex02_oral_1 | 400 mg | h, ng/mL | 0 / 33 | 0 / 33 | 8 / 8 | 0 | 5 / 5 | 8.4 |
| ex03_pk2_iv_bolus | 300 mg | h, mg/L | 0 / 41 | 0 / 41 | 8 / 8 | 0 | 5 / 5 | 10.1 |
| ex04_oral_1_lag | 300 mg | h, ng/mL | 0 / 41 | 0 / 41 | 8 / 8 | 0 | 8 / 8 | 11.8 |
| ex05_iv_infusion | 150 mg | h, mg/L | 0 / 38 | 0 / 38 | 8 / 8 | 0 | 5 / 5 | 8.5 |
| ex06_oral_0 | 100 mg | h, ng/mL | 0 / 32 | 0 / 32 | 8 / 8 | 0 | 5 / 5 | 8.2 |
| ex07_iv_bolus | 2000 ug | h, ng/mL | 0 / 52 | 0 / 52 | 8 / 8 | 0 | 9 / 9 | 15.1 |
| ex08_oral_1 | 800 ug | min, ng/mL | 0 / 32 | 0 / 32 | 8 / 8 | 0 | 5 / 5 | 7.9 |
| ex09_pk2_oral_1 | 300 mg | h, ng/mL | 0 / 33 | 0 / 33 | 8 / 8 | 0 | 7 / 7 | 10.2 |
| ex10_oral_1_lag | 100 mg | h, mg/L | 0 / 33 | 0 / 33 | 8 / 8 | 0 | 5 / 5 | 8.8 |
| ex11_pk2_iv_bolus | 1000 ug | h, ng/mL | 0 / 46 | 0 / 46 | 8 / 8 | 0 | 7 / 7 | 14.2 |
| ex12_iv_infusion | 500 ug | min, ng/mL | 0 / 27 | 0 / 27 | 7 / 8 | 0 | 10 / 10 | 11.5 |
| ex13_oral_1 | 50 mg | h, ng/mL | 0 / 45 | 0 / 45 | 8 / 8 | 0 | 6 / 6 | 10.2 |
| ex14_iv_bolus | 150 mg | h, ng/mL | 0 / 39 | 0 / 39 | 8 / 8 | 0 | 9 / 9 | 13.8 |
| ex15_oral_0 | 400 mg | h, mg/L | 0 / 38 | 0 / 38 | 8 / 8 | 0 | 6 / 6 | 9.1 |
| ex16_pk2_oral_1 | 2000 ug | h, ng/mL | 0 / 42 | 0 / 42 | 8 / 8 | 0 | 5 / 5 | 9.2 |
| ex17_oral_1 | 500 mg | h, mg/L | 0 / 33 | 0 / 33 | 7 / 8 | 0 | 6 / 6 | 8.8 |
| ex18_pk2_iv_bolus | 200 mg | min, ng/mL | 0 / 41 | 0 / 41 | 8 / 8 | 0 | 9 / 9 | 14.5 |
| ex19_oral_1_lag | 2000 ug | h, ng/mL | 0 / 33 | 0 / 33 | 8 / 8 | 0 | 7 / 7 | 11.7 |
| ex20_iv_infusion | 150 mg | h, ng/mL | 0 / 34 | 0 / 34 | 8 / 8 | 0 | 5 / 5 | 8.5 |
| ex21_oral_0 | 5000 ug | h, ng/mL | 0 / 32 | 0 / 32 | 8 / 8 | 0 | 5 / 5 | 8.1 |
| ex22_pk2_oral_1 | 500 mg | h, mg/L | 0 / 33 | 0 / 33 | 7 / 8 | 0 | 5 / 5 | 8.5 |
| ex23_iv_bolus | 300 mg | min, ng/mL | 0 / 43 | 0 / 43 | 7 / 8 | 0 | 9 / 9 | 14.1 |
| ex24_pk2_iv_bolus | 150 mg | h, ng/mL | 0 / 29 | 0 / 29 | 8 / 8 | 0 | 5 / 5 | 8.7 |
| ex25_oral_1 | 100 mg | h, ng/mL | 0 / 32 | 0 / 32 | 7 / 8 | 0 | 7 / 7 | 11.9 |
