# Schema report of decision/ood/requests.jsonl

Lines converted: 74. Lines rejected: 0. Converted rows are in `decision/ood/rows.jsonl` (typed-decisions format, split `ood`, 20 questions per row).

## Warnings (converted, but worth a look)

| id | warning |
|---|---|
| ood-002 | prior analysis ids renumbered {"1": 2} (engine numbering) |
| ood-003 | prior analysis ids renumbered {"1": 2} (engine numbering) |
| ood-009 | prior analysis ids renumbered {"1": 2} (engine numbering) |
| ood-013 | gold analysis and compare_pair disagree (a pair is named only by a compare request) |
| ood-013 | prior analysis ids renumbered {"1": 2} (engine numbering) |
| ood-014 | prior analysis ids renumbered {"1": 2, "2": 3} (engine numbering) |
| ood-015 | prior analysis ids renumbered {"1": 2, "2": 3} (engine numbering) |
| ood-019 | is_not_available is true but asked is empty (the refusal names no parameter) |
| ood-020 | is_not_available is true but asked is empty (the refusal names no parameter) |
| ood-025 | prior analysis ids renumbered {"1": 2} (engine numbering) |
| ood-030 | gold analysis and compare_pair disagree (a pair is named only by a compare request) |
| ood-030 | prior analysis ids renumbered {"1": 2} (engine numbering) |
| ood-034 | is_not_available is true but asked is empty (the refusal names no parameter) |
| ood-048 | is_not_available is true but asked is empty (the refusal names no parameter) |
| ood-056 | prior analysis ids renumbered {"1": 2} (engine numbering) |
| ood-057 | prior analysis ids renumbered {"1": 2, "2": 3} (engine numbering) |
| ood-058 | gold analysis and compare_pair disagree (a pair is named only by a compare request) |
| ood-064 | is_not_available is true but asked is empty (the refusal names no parameter) |
| ood-065 | is_not_available is true but asked is empty (the refusal names no parameter) |
| ood-071 | gold analysis and compare_pair disagree (a pair is named only by a compare request) |
| ood-071 | prior analysis ids renumbered {"1": 2} (engine numbering) |
| ood-072 | prior analysis ids renumbered {"1": 2, "2": 3} (engine numbering) |

## Coverage

Rows per exercise: ex01_iv_bolus 4, ex02_oral_1 10, ex03_pk2_iv_bolus 5, ex04_oral_1_lag 2, ex05_iv_infusion 4, ex06_oral_0 3, ex07_iv_bolus 4, ex08_oral_1 4, ex09_pk2_oral_1 2, ex10_oral_1_lag 1, ex11_pk2_iv_bolus 1, ex12_iv_infusion 3, ex13_oral_1 2, ex14_iv_bolus 2, ex16_pk2_oral_1 1, ex17_oral_1 1, ex18_pk2_iv_bolus 2, ex20_iv_infusion 1, ex21_oral_0 1, ex22_pk2_oral_1 1, ex23_iv_bolus 1, ex24_pk2_iv_bolus 1, ex25_oral_1 2, oodx01_oral_mg_ugml 2, oodx02_iv_bolus_tlag 2, oodx03_oral_c0 2, oodx04_infusion_dur_h 1, oodx05_two_subjects 1, oodx06_steady_state 1, oodx07_urine 1, oodx08_pk2_oral_fit 1, oodx09_oral_min_ng 2, oodx10_oral_blq 1, oodx11_oral_dose_g 1, oodx12_iv_infusion_mcg 1.

Rows per tag: abbreviation 17, bioequivalence 1, blq 4, by-id 2, c0 1, colloquial 6, compare 8, dose-unit-g 1, dose-unit-mcg 1, dose-unit-mg 1, dose-unit-micro 9, dose-without-unit 1, duration-unit-mismatch 2, duration-word 1, english-term 1, fit 4, follow-up 4, infusion 7, invented 16, iv-explicit 1, language-mix 2, latin-route 3, method-explicit 2, multi-subject 1, multiple-dose 1, no-dose 1, no-parameter 1, no-prior-analysis 1, non-auc-parameter 1, oral 1, out-of-scope 4, parameter-not-for-route 5, parameter-not-in-schema 2, plain 2, population 1, recall 1, rerun 4, route-implied 5, route-missing 1, route-stated 8, simulate 1, steady-state 1, terminology-mismatch 2, tlag 1, two-compartments 2, two-requests-in-one-sentence 2, typo 2, unicode 1, unit-conversion-in-text 1, unit-in-text 5, unit-variety 1, unrecognized-unit 1, urine 1.

Gold `analysis`: compare 8, fit_pk1 1, fit_pk2 3, nca 45, none_needed 16, simulate 1.
Gold `route`: iv_bolus 22, iv_infusion 10, oral 40, unknown 2.
Gold `auc_method`: lin_up_log_down 8, linear 57, not_applicable 9.
Gold `compare_pair`: 2+3 4, not_applicable 70.
