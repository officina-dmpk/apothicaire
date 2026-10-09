# Apothicaire benchmark report: decision harness

date: 2026-10-09-dsh-model, exercises_run: 25, model: decision harness (decision/harness.py), decider decider_unsloth:decide

**Hallucination rate = numbers not found in a tool result or user message / numbers checked (deterministic gate `gate.py`).**

- before the gate's regeneration (first drafts): **0 / 0 = n/a**
- in the answers shown (gate in the loop): **0 / 0 = n/a**
- 25 exercises, 200 turns (200 failed by an error); turns with an unverified number: 0 before, 0 after; regenerated 0 (regeneration kept 0); turns shown with the badge: 0

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
| unit_conversion | 3.2 % | 1.6 % |
| arithmetic | 0.0 % | 4.7 % |
| unlabelled_misread | 8.5 % | 9.6 % |
| recall_error | 0.0 % | 0.0 % |
| other | 88.3 % | 84.1 % |

## Correctness: 0 / 0 turns fully correct; expected numbers found 0 / 0; forbidden (converted or computed) values present in 0 answers

| question type | turns | correct | found / expected numbers | unverified / total before | unverified / total shown |
|---|---|---|---|---|---|

## Oracle check: no stored oracle verdicts (run `run_bench.py --rescore`)

## Tool calls: 0 valid, 0 invalid, 0 failed of 0 (validity n/a)

`nca_run` calls: 0, with the right dose 0, with the right route 0; memory calls (zoom / read_message): 0; by tool: {}. invalid = unknown tool, invalid_parameters, unknown_worksheet / unknown_analysis or any rejection; failed = accepted but the analysis errs for every subject.

## Time: n/a

## Per exercise

| exercise | dose | units | unverified / total before | unverified / total shown | correct turns | badge turns | calls valid / total | mean s per turn |
|---|---|---|---|---|---|---|---|---|
| ex01_iv_bolus | 200 mg | h, mg/L | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex02_oral_1 | 400 mg | h, ng/mL | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex03_pk2_iv_bolus | 300 mg | h, mg/L | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex04_oral_1_lag | 300 mg | h, ng/mL | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex05_iv_infusion | 150 mg | h, mg/L | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex06_oral_0 | 100 mg | h, ng/mL | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex07_iv_bolus | 2000 ug | h, ng/mL | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex08_oral_1 | 800 ug | min, ng/mL | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex09_pk2_oral_1 | 300 mg | h, ng/mL | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex10_oral_1_lag | 100 mg | h, mg/L | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex11_pk2_iv_bolus | 1000 ug | h, ng/mL | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex12_iv_infusion | 500 ug | min, ng/mL | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex13_oral_1 | 50 mg | h, ng/mL | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex14_iv_bolus | 150 mg | h, ng/mL | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex15_oral_0 | 400 mg | h, mg/L | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex16_pk2_oral_1 | 2000 ug | h, ng/mL | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex17_oral_1 | 500 mg | h, mg/L | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex18_pk2_iv_bolus | 200 mg | min, ng/mL | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex19_oral_1_lag | 2000 ug | h, ng/mL | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex20_iv_infusion | 150 mg | h, ng/mL | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex21_oral_0 | 5000 ug | h, ng/mL | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex22_pk2_oral_1 | 500 mg | h, mg/L | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex23_iv_bolus | 300 mg | min, ng/mL | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex24_pk2_iv_bolus | 150 mg | h, ng/mL | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |
| ex25_oral_1 | 100 mg | h, ng/mL | 0 / 0 | 0 / 0 | 0 / 0 | 0 | 0 / 0 | n/a |

## Decision harness

No turn.

Answers outside the options offered by the question set (left unused by the harness): none.

Harness notes: none.

## Decision model

- model: None
- load_s: 0.0
- decide_calls: 0
- model_seconds_total: 0.0
- model_seconds_per_call: 0.0
- torch_peak_allocated_mib: 8
- nvidia_smi_used_mib_at_end: 1348
