# Apothicaire benchmark report: decision harness

date: 2026-10-09, exercises_run: 25, model: decision harness (decision/harness.py), decider decider_unsloth:decide

**Hallucination rate = numbers not found in a tool result or user message / numbers checked (deterministic gate `gate.py`).**

- before the gate's regeneration (first drafts): **0 / 709 = 0.0 %** (none observed: upper 95 % bound by the rule of three 3/709 = 0.42 %)
- in the answers shown (gate in the loop): **0 / 709 = 0.0 %** (none observed: upper 95 % bound by the rule of three 3/709 = 0.42 %)
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
| unlabelled_misread | 11.7 % | 8.3 % |
| recall_error | 0.0 % | 0.0 % |
| other | 77.4 % | 65.8 % |

## Correctness: 200 / 200 turns fully correct; expected numbers found 558 / 558; forbidden (converted or computed) values present in 0 answers

| question type | turns | correct | found / expected numbers | unverified / total before | unverified / total shown |
|---|---|---|---|---|---|
| import_nca | 25 | 25 (100.0 %) | 225 / 225 | 0 / 251 | 0 / 251 |
| cmax_tmax | 25 | 25 (100.0 %) | 58 / 58 | 0 / 84 | 0 / 84 |
| clearance_volume | 25 | 25 (100.0 %) | 50 / 50 | 0 / 76 | 0 / 76 |
| half_life | 25 | 25 (100.0 %) | 50 / 50 | 0 / 76 | 0 / 76 |
| lambda_z_regression | 25 | 25 (100.0 %) | 50 / 50 | 0 / 51 | 0 / 51 |
| recall | 25 | 25 (100.0 %) | 25 / 25 | 0 / 28 | 0 / 28 |
| compare | 25 | 25 (100.0 %) | 100 / 100 | 0 / 125 | 0 / 125 |
| not_available | 25 | 25 (100.0 %) | 0 / 0 | 0 / 18 | 0 / 18 |

## Compare turn and `analysis_compare`: called in 25 of 25 compare turns (25 calls, 25 valid; 25 calls in all turns); usable in 25 (the two analyses of the exercise, the auclast row with difference and percentage, equal to the ground-truth arithmetic: then the engine's difference and percentage are expected and allowed, other computed values stay forbidden); row disagreeing with the ground truth: 0; no call: 0


## Oracle check: 175 / 175 turns = 100.0 %; 558 / 558 expected numbers = 100.0 %

Second judgement, independent of the gate (`bench/score.py`, `oracle_turn`): the number written after the label of the parameter the question asks for must be Caladrius's value of THAT parameter, of the right AUC method, with the unit Caladrius reports. The gate counts above are untouched; the denominators here are the turns that expect numbers and the numbers they expect (not covered: not_available, no value to check).

| question type | turns | oracle-correct | expected numbers ok | wrong_parameter | wrong_method | wrong_option | missing_unit | wrong_unit | missing_value |
|---|---|---|---|---|---|---|---|---|---|
| import_nca | 25 | 25 (100.0 %) | 225 / 225 | 0 | 0 | 0 | 0 | 0 | 0 |
| cmax_tmax | 25 | 25 (100.0 %) | 58 / 58 | 0 | 0 | 0 | 0 | 0 | 0 |
| clearance_volume | 25 | 25 (100.0 %) | 50 / 50 | 0 | 0 | 0 | 0 | 0 | 0 |
| half_life | 25 | 25 (100.0 %) | 50 / 50 | 0 | 0 | 0 | 0 | 0 | 0 |
| lambda_z_regression | 25 | 25 (100.0 %) | 50 / 50 | 0 | 0 | 0 | 0 | 0 | 0 |
| recall | 25 | 25 (100.0 %) | 25 / 25 | 0 | 0 | 0 | 0 | 0 | 0 |
| compare | 25 | 25 (100.0 %) | 100 / 100 | 0 | 0 | 0 | 0 | 0 | 0 |
| **total** | 175 | 175 (100.0 %) | 558 / 558 | 0 | 0 | 0 | 0 | 0 | 0 |

Against the scorer's expected-number check (the global search of the numbers, above): items the scorer found but the oracle rejects 0; items the scorer missed but the oracle accepts 0; turns oracle-wrong but scorer-correct 0; turns oracle-correct but scorer-incorrect 0.

## Tool calls: 250 valid, 0 invalid, 0 failed of 250 (validity 100.0 %)

`nca_run` calls: 50, with the right dose 50, with the right route 50; memory calls (zoom / read_message): 0; by tool: {'analysis_compare': 25, 'analysis_get': 150, 'data_import': 25, 'nca_run': 50}. invalid = unknown tool, invalid_parameters, unknown_worksheet / unknown_analysis or any rejection; failed = accepted but the analysis errs for every subject.

## Tool-call argument audit: 0 of 75 `nca_run` / `data_import` calls differ from the exercise's intent (dose, route, AUC method alone as options; the CSV and the column units)

No deviation.

## Time: mean 0.3 s per turn, mean 0 prompt tokens (first call), total 1 min

## Per exercise

| exercise | dose | units | unverified / total before | unverified / total shown | correct turns | badge turns | calls valid / total | mean s per turn |
|---|---|---|---|---|---|---|---|---|
| ex01_iv_bolus | 200 mg | h, mg/L | 0 / 29 | 0 / 29 | 8 / 8 | 0 | 10 / 10 | 3.7 |
| ex02_oral_1 | 400 mg | h, ng/mL | 0 / 28 | 0 / 28 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex03_pk2_iv_bolus | 300 mg | h, mg/L | 0 / 29 | 0 / 29 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex04_oral_1_lag | 300 mg | h, ng/mL | 0 / 28 | 0 / 28 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex05_iv_infusion | 150 mg | h, mg/L | 0 / 35 | 0 / 35 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex06_oral_0 | 100 mg | h, ng/mL | 0 / 28 | 0 / 28 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex07_iv_bolus | 2000 ug | h, ng/mL | 0 / 23 | 0 / 23 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex08_oral_1 | 800 ug | min, ng/mL | 0 / 28 | 0 / 28 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex09_pk2_oral_1 | 300 mg | h, ng/mL | 0 / 28 | 0 / 28 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex10_oral_1_lag | 100 mg | h, mg/L | 0 / 28 | 0 / 28 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex11_pk2_iv_bolus | 1000 ug | h, ng/mL | 0 / 28 | 0 / 28 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex12_iv_infusion | 500 ug | min, ng/mL | 0 / 33 | 0 / 33 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex13_oral_1 | 50 mg | h, ng/mL | 0 / 28 | 0 / 28 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex14_iv_bolus | 150 mg | h, ng/mL | 0 / 33 | 0 / 33 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex15_oral_0 | 400 mg | h, mg/L | 0 / 28 | 0 / 28 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex16_pk2_oral_1 | 2000 ug | h, ng/mL | 0 / 22 | 0 / 22 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex17_oral_1 | 500 mg | h, mg/L | 0 / 28 | 0 / 28 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex18_pk2_iv_bolus | 200 mg | min, ng/mL | 0 / 28 | 0 / 28 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex19_oral_1_lag | 2000 ug | h, ng/mL | 0 / 22 | 0 / 22 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex20_iv_infusion | 150 mg | h, ng/mL | 0 / 35 | 0 / 35 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex21_oral_0 | 5000 ug | h, ng/mL | 0 / 28 | 0 / 28 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex22_pk2_oral_1 | 500 mg | h, mg/L | 0 / 28 | 0 / 28 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex23_iv_bolus | 300 mg | min, ng/mL | 0 / 28 | 0 / 28 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex24_pk2_iv_bolus | 150 mg | h, ng/mL | 0 / 28 | 0 / 28 | 8 / 8 | 0 | 10 / 10 | 0.2 |
| ex25_oral_1 | 100 mg | h, ng/mL | 0 / 28 | 0 / 28 | 8 / 8 | 0 | 10 / 10 | 0.2 |

## Decision harness

225 decide calls in 200 turns; mean 0.337 s per turn (engine calls and rendering; no prompt tokens; with a trained decider the time includes its forward passes, see the decision model section if any).

Answers outside the options offered by the question set (left unused by the harness): none.

Harness notes: none.

## Decision model

- model: C:\Users\abdou\apothicaire\agent\decision\models\qwen35-0.8b-d01\merged
- load_s: 6.9
- decide_calls: 225
- model_seconds_total: 44.25
- model_seconds_per_call: 0.1966
- torch_peak_allocated_mib: 1936
- nvidia_smi_used_mib_at_end: 2859
