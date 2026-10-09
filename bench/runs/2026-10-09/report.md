# Apothicaire benchmark report

date: 2026-10-09, exercises_run: 25, model: Bonsai 2 27B (Ternary-Bonsai-2-27B-PTQ1_0), temperature 0.3, no fixed seed

**Hallucination rate = numbers not found in a tool result or user message / numbers checked (deterministic gate `gate.py`).**

- before the gate's regeneration (first drafts): **76 / 932 = 8.2 %** (95 % CI, exercises resampled: 7.1-9.1 %)
- in the answers shown (gate in the loop): **0 / 827 = 0.0 %** (none observed: upper 95 % bound by the rule of three 3/827 = 0.36 %)
- 25 exercises, 200 turns (0 failed by an error); turns with an unverified number: 25 before, 0 after; regenerated 25 (regeneration kept 25); turns shown with the badge: 0

## Failure taxonomy (unverified numbers)

| class | before the gate | in the answers shown |
|---|---|---|
| unit_conversion | 1 | 0 |
| arithmetic | 58 | 0 |
| unlabelled_misread | 1 | 0 |
| recall_error | 0 | 0 |
| other | 16 | 0 |

Classes are heuristics (`bench/score.py`); the unverified counts above never depend on them. Chance baseline: how the same rules classify random numbers of 3 and 4 significant digits drawn over each exercise's range of tool values (a class whose baseline share is large is weak evidence at that precision):

| class | random 3-digit numbers | random 4-digit numbers |
|---|---|---|
| unit_conversion | 10.6 % | 3.4 % |
| arithmetic | 0.0 % | 21.7 % |
| unlabelled_misread | 10.6 % | 7.8 % |
| recall_error | 0.0 % | 0.0 % |
| other | 78.8 % | 67.1 % |

## Correctness: 193 / 200 turns fully correct; expected numbers found 496 / 508; forbidden (converted or computed) values present in 0 answers

| question type | turns | correct | found / expected numbers | unverified / total before | unverified / total shown |
|---|---|---|---|---|---|
| import_nca | 25 | 23 (92.0 %) | 220 / 225 | 0 / 428 | 0 / 428 |
| cmax_tmax | 25 | 25 (100.0 %) | 58 / 58 | 0 / 59 | 0 / 59 |
| clearance_volume | 25 | 24 (96.0 %) | 48 / 50 | 0 / 54 | 0 / 54 |
| half_life | 25 | 24 (96.0 %) | 49 / 50 | 0 / 121 | 0 / 121 |
| lambda_z_regression | 25 | 25 (100.0 %) | 50 / 50 | 0 / 74 | 0 / 74 |
| recall | 25 | 24 (96.0 %) | 25 / 25 | 0 / 28 | 0 / 28 |
| compare | 25 | 23 (92.0 %) | 46 / 50 | 76 / 168 | 0 / 63 |
| not_available | 25 | 25 (100.0 %) | 0 / 0 | 0 / 0 | 0 / 0 |

## Oracle check: 168 / 175 turns = 96.0 % (95 % CI, exercises resampled: 89.7-100.0 %); 494 / 508 expected numbers = 97.2 % (95 % CI, exercises resampled: 92.3-100.0 %)

Second judgement, independent of the gate (`bench/score.py`, `oracle_turn`): the number written after the label of the parameter the question asks for must be Caladrius's value of THAT parameter, of the right AUC method, with the unit Caladrius reports. The gate counts above are untouched; the denominators here are the turns that expect numbers and the numbers they expect (not covered: not_available, no value to check).

| question type | turns | oracle-correct | expected numbers ok | wrong_parameter | wrong_method | wrong_option | missing_unit | wrong_unit | missing_value |
|---|---|---|---|---|---|---|---|---|---|
| import_nca | 25 | 23 (92.0 %) | 219 / 225 | 1 | 0 | 5 | 0 | 0 | 0 |
| cmax_tmax | 25 | 25 (100.0 %) | 58 / 58 | 0 | 0 | 0 | 0 | 0 | 0 |
| clearance_volume | 25 | 24 (96.0 %) | 48 / 50 | 0 | 0 | 2 | 0 | 0 | 0 |
| half_life | 25 | 24 (96.0 %) | 49 / 50 | 0 | 0 | 1 | 0 | 0 | 0 |
| lambda_z_regression | 25 | 25 (100.0 %) | 50 / 50 | 0 | 0 | 0 | 0 | 0 | 0 |
| recall | 25 | 24 (96.0 %) | 24 / 25 | 0 | 0 | 0 | 1 | 0 | 0 |
| compare | 25 | 23 (92.0 %) | 46 / 50 | 2 | 0 | 2 | 0 | 0 | 0 |
| **total** | 175 | 168 (96.0 %) | 494 / 508 | 3 | 0 | 10 | 1 | 0 | 0 |

Against the scorer's expected-number check (the global search of the numbers, above): items the scorer found but the oracle rejects 2 (ex07_iv_bolus t1 CL (wrong_option); ex21_oral_0 t6 dose (missing_unit)); items the scorer missed but the oracle accepts 0; turns oracle-wrong but scorer-correct 0; turns oracle-correct but scorer-incorrect 0.

Every expected number the oracle rejects:

| exercise | turn | expected | class | detail | numbers written after the label |
|---|---|---|---|---|---|
| ex07_iv_bolus | 1 import_nca | AUC(0-tlast) | wrong_option | options.start=zero | 159,97 h*ng/ml, 159,97 h*ng/ml, 23 h, 20 % |
| ex07_iv_bolus | 1 import_nca | AUC(0-inf) | wrong_option | options.start=zero | 164,88 h*ng/ml, 164,88 h*ng/ml, 3,2 h, 7 |
| ex07_iv_bolus | 1 import_nca | CL | wrong_option | options.start=zero | 12,13 doseunit/(h*ng/ml), 12,13 h*ng/ml |
| ex07_iv_bolus | 1 import_nca | Vz | wrong_option | options.start=zero | 77,88 doseunit/(ng/ml), 77,88 µg/(ng/ml) |
| ex07_iv_bolus | 1 import_nca | MRT | wrong_option | options.start=zero | 7,07 h, 7,07 h |
| ex07_iv_bolus | 3 clearance_volume | CL | wrong_option | options.start=zero | 12,13 doseunit/(h*ng/ml) |
| ex07_iv_bolus | 3 clearance_volume | Vz | wrong_option | options.start=zero | 77,88 doseunit/(ng/ml) |
| ex07_iv_bolus | 4 half_life | AUC % extrapolated | wrong_option | options.start=zero | 2,98 %, 0, 2,98 % |
| ex07_iv_bolus | 7 compare | AUC(0-tlast) linear | wrong_option | options.start=zero | 159,967 h*ng/ml |
| ex07_iv_bolus | 7 compare | AUC(0-tlast) lin-up/log-down | wrong_option | options.start=zero | 157,492 h*ng/ml |
| ex13_oral_1 | 1 import_nca | AUC(0-tlast) | wrong_parameter | aucall | 3152.57 h*ng/ml |
| ex13_oral_1 | 7 compare | AUC(0-tlast) linear | wrong_parameter | aucall | 3152.57 h*ng/ml |
| ex13_oral_1 | 7 compare | AUC(0-tlast) lin-up/log-down | wrong_parameter | aucall | 3056.08 h*ng/ml |
| ex21_oral_0 | 6 recall | dose | missing_unit |  | 5000 |

## Tool calls: 112 valid, 2 invalid, 0 failed of 114 (validity 98.2 %)

`nca_run` calls: 50, with the right dose 50, with the right route 50; memory calls (zoom / read_message): 6; by tool: {'analysis_get': 38, 'data_import': 26, 'nca_run': 50}. invalid = unknown tool, invalid_parameters, unknown_worksheet / unknown_analysis or any rejection; failed = accepted but the analysis errs for every subject.

## Tool-call argument audit: 3 of 76 `nca_run` / `data_import` calls differ from the exercise's intent (dose, route, AUC method alone as options; the CSV and the column units)

| deviation | calls |
|---|---|
| nca_run: options.start = "zero" (intended null) | 2 |
| data_import: csv = "<95 chars, DIFFERENT from the exercise CSV>" (intended "identical to the exercise CSV") | 1 |

In exercises: ex07_iv_bolus, ex23_iv_bolus. A deviation is listed here whatever its effect; the oracle check calls it `wrong_option` only when the answer's value is wrong (`run_bench.py --tool-arg-audit` prints every call).

## Time: mean 10.1 s per turn, mean 4289 prompt tokens (first call), total 64 min

## Per exercise

| exercise | dose | units | unverified / total before | unverified / total shown | correct turns | badge turns | calls valid / total | mean s per turn |
|---|---|---|---|---|---|---|---|---|
| ex01_iv_bolus | 200 mg | h, mg/L | 5 / 48 | 0 / 40 | 8 / 8 | 0 | 9 / 9 | 16.3 |
| ex02_oral_1 | 400 mg | h, ng/mL | 5 / 43 | 0 / 34 | 8 / 8 | 0 | 4 / 4 | 9.4 |
| ex03_pk2_iv_bolus | 300 mg | h, mg/L | 4 / 38 | 0 / 31 | 8 / 8 | 0 | 5 / 5 | 11.0 |
| ex04_oral_1_lag | 300 mg | h, ng/mL | 5 / 37 | 0 / 29 | 8 / 8 | 0 | 4 / 4 | 8.6 |
| ex05_iv_infusion | 150 mg | h, mg/L | 2 / 34 | 0 / 32 | 8 / 8 | 0 | 4 / 4 | 8.3 |
| ex06_oral_0 | 100 mg | h, ng/mL | 2 / 35 | 0 / 33 | 8 / 8 | 0 | 4 / 4 | 9.0 |
| ex07_iv_bolus | 2000 ug | h, ng/mL | 4 / 46 | 0 / 39 | 4 / 8 | 0 | 4 / 4 | 11.0 |
| ex08_oral_1 | 800 ug | min, ng/mL | 2 / 33 | 0 / 31 | 8 / 8 | 0 | 4 / 4 | 8.8 |
| ex09_pk2_oral_1 | 300 mg | h, ng/mL | 2 / 29 | 0 / 27 | 8 / 8 | 0 | 7 / 7 | 11.1 |
| ex10_oral_1_lag | 100 mg | h, mg/L | 2 / 40 | 0 / 38 | 8 / 8 | 0 | 4 / 4 | 9.4 |
| ex11_pk2_iv_bolus | 1000 ug | h, ng/mL | 2 / 36 | 0 / 34 | 8 / 8 | 0 | 5 / 5 | 11.0 |
| ex12_iv_infusion | 500 ug | min, ng/mL | 3 / 44 | 0 / 39 | 8 / 8 | 0 | 4 / 4 | 10.0 |
| ex13_oral_1 | 50 mg | h, ng/mL | 2 / 37 | 0 / 35 | 6 / 8 | 0 | 4 / 4 | 9.3 |
| ex14_iv_bolus | 150 mg | h, ng/mL | 4 / 40 | 0 / 35 | 8 / 8 | 0 | 4 / 4 | 12.4 |
| ex15_oral_0 | 400 mg | h, mg/L | 4 / 35 | 0 / 28 | 8 / 8 | 0 | 4 / 4 | 9.1 |
| ex16_pk2_oral_1 | 2000 ug | h, ng/mL | 4 / 41 | 0 / 36 | 8 / 8 | 0 | 4 / 4 | 9.9 |
| ex17_oral_1 | 500 mg | h, mg/L | 2 / 32 | 0 / 30 | 8 / 8 | 0 | 4 / 4 | 8.2 |
| ex18_pk2_iv_bolus | 200 mg | min, ng/mL | 2 / 33 | 0 / 31 | 8 / 8 | 0 | 4 / 4 | 9.3 |
| ex19_oral_1_lag | 2000 ug | h, ng/mL | 4 / 39 | 0 / 32 | 8 / 8 | 0 | 4 / 5 | 9.6 |
| ex20_iv_infusion | 150 mg | h, ng/mL | 3 / 43 | 0 / 38 | 8 / 8 | 0 | 4 / 4 | 9.3 |
| ex21_oral_0 | 5000 ug | h, ng/mL | 5 / 40 | 0 / 32 | 7 / 8 | 0 | 7 / 7 | 14.4 |
| ex22_pk2_oral_1 | 500 mg | h, mg/L | 2 / 36 | 0 / 36 | 8 / 8 | 0 | 4 / 4 | 9.8 |
| ex23_iv_bolus | 300 mg | min, ng/mL | 2 / 31 | 0 / 29 | 8 / 8 | 0 | 4 / 5 | 10.7 |
| ex24_pk2_iv_bolus | 150 mg | h, ng/mL | 2 / 32 | 0 / 30 | 8 / 8 | 0 | 3 / 3 | 9.6 |
| ex25_oral_1 | 100 mg | h, ng/mL | 2 / 30 | 0 / 28 | 8 / 8 | 0 | 4 / 4 | 8.3 |
