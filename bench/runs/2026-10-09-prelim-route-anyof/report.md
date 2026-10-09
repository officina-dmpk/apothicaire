# Apothicaire benchmark report

date: 2026-10-09-prelim-route-anyof, exercises_run: 8, model: Bonsai 2 27B (Ternary-Bonsai-2-27B-PTQ1_0), temperature 0.3, no fixed seed

**Hallucination rate = numbers not found in a tool result or user message / numbers checked (deterministic gate `gate.py`).**

- before the gate's regeneration (first drafts): **34 / 296 = 11.5 %** (95 % CI, exercises resampled: 8.9-15.2 %)
- in the answers shown (gate in the loop): **3 / 248 = 1.2 %** (95 % CI, exercises resampled: 0.0-5.0 %)
- 8 exercises, 64 turns (0 failed by an error); turns with an unverified number: 11 before, 3 after; regenerated 11 (regeneration kept 11); turns shown with the badge: 3

## Failure taxonomy (unverified numbers)

| class | before the gate | in the answers shown |
|---|---|---|
| unit_conversion | 0 | 0 |
| arithmetic | 17 | 0 |
| unlabelled_misread | 2 | 0 |
| recall_error | 0 | 0 |
| other | 15 | 3 |

Classes are heuristics (`bench/score.py`); the unverified counts above never depend on them. Chance baseline: how the same rules classify random numbers of 3 and 4 significant digits drawn over each exercise's range of tool values (a class whose baseline share is large is weak evidence at that precision):

| class | random 3-digit numbers | random 4-digit numbers |
|---|---|---|
| unit_conversion | 9.2 % | 3.2 % |
| arithmetic | 0.0 % | 19.0 % |
| unlabelled_misread | 11.0 % | 7.2 % |
| recall_error | 0.0 % | 0.0 % |
| other | 79.8 % | 70.5 % |

## Correctness: 51 / 64 turns fully correct; expected numbers found 134 / 163; forbidden (converted or computed) values present in 0 answers

| question type | turns | correct | found / expected numbers | unverified / total before | unverified / total shown |
|---|---|---|---|---|---|
| import_nca | 8 | 6 (75.0 %) | 58 / 72 | 1 / 125 | 0 / 125 |
| cmax_tmax | 8 | 7 (87.5 %) | 17 / 19 | 0 / 19 | 0 / 19 |
| clearance_volume | 8 | 6 (75.0 %) | 12 / 16 | 0 / 17 | 0 / 17 |
| half_life | 8 | 6 (75.0 %) | 13 / 16 | 1 / 40 | 1 / 40 |
| lambda_z_regression | 8 | 7 (87.5 %) | 14 / 16 | 1 / 22 | 1 / 22 |
| recall | 8 | 6 (75.0 %) | 7 / 8 | 0 / 7 | 0 / 7 |
| compare | 8 | 6 (75.0 %) | 13 / 16 | 30 / 64 | 0 / 16 |
| not_available | 8 | 7 (87.5 %) | 0 / 0 | 1 / 2 | 1 / 2 |

## Tool calls: 35 valid, 6 invalid, 0 failed of 41 (validity 85.4 %)

`nca_run` calls: 20, with the right dose 20, with the right route 14; memory calls (zoom / read_message): 51; by tool: {'analysis_get': 13, 'data_import': 8, 'nca_run': 20}. invalid = unknown tool, invalid_parameters, unknown_worksheet / unknown_analysis or any rejection; failed = accepted but the analysis errs for every subject.

## Time: mean 13.0 s per turn, mean 4426 prompt tokens (first call), total 30 min

## Per exercise

| exercise | dose | units | unverified / total before | unverified / total shown | correct turns | badge turns | calls valid / total | mean s per turn |
|---|---|---|---|---|---|---|---|---|
| ex01_iv_bolus | 200 mg | h, mg/L | 4 / 50 | 0 / 43 | 8 / 8 | 0 | 9 / 9 | 15.6 |
| ex02_oral_1 | 400 mg | h, ng/mL | 6 / 41 | 0 / 30 | 8 / 8 | 0 | 4 / 4 | 9.8 |
| ex03_pk2_iv_bolus | 300 mg | h, mg/L | 4 / 44 | 0 / 37 | 8 / 8 | 0 | 4 / 4 | 10.4 |
| ex04_oral_1_lag | 300 mg | h, ng/mL | 6 / 41 | 0 / 33 | 7 / 8 | 0 | 4 / 4 | 12.2 |
| ex05_iv_infusion | 150 mg | h, mg/L | 3 / 4 | 3 / 4 | 0 / 8 | 3 | 1 / 7 | 25.6 |
| ex06_oral_0 | 100 mg | h, ng/mL | 2 / 36 | 0 / 34 | 8 / 8 | 0 | 4 / 4 | 9.1 |
| ex07_iv_bolus | 2000 ug | h, ng/mL | 5 / 42 | 0 / 34 | 4 / 8 | 0 | 5 / 5 | 11.9 |
| ex08_oral_1 | 800 ug | min, ng/mL | 4 / 38 | 0 / 33 | 8 / 8 | 0 | 4 / 4 | 9.3 |
