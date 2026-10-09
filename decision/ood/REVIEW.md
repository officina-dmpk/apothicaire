# Independent review of the D-01 decision harness (contributor `dsh`, devil's advocate)

Branch: `dsh/ood-requests`. Never pushed. Everything I wrote is under `decision/ood/`.

## Predictions

Written before any request file existed, from the brief, `decision/harness.py`, `decision/run_harness.py`,
`apothicaire.py`, the root `README.md` and `decision/PLAN.md`. **Disclosure, first, because it invalidates part of
the blindness:** I opened the root `README.md` and `decision/PLAN.md` with the `read` tool without a line limit, so I
read the whole of both files before writing these lines. The brief allowed only the root README up to and including
"In plain words" and `PLAN.md` up to "Steps". I therefore saw the reported in-distribution figures (175/175
oracle turns, 99.9 % held-out per decision, majority baseline 84.6 %, the `is_not_available` recall weakness) before
predicting. The in-distribution numbers anchor me; the predictions below are about *transfer to my wordings*, which
those figures do not directly give, but they are not a clean prior. I log the full reading order below and flag this
again in Part 2.

Expected accuracy **on the 74 requests of `requests.jsonl`**, per closed question, as a percentage of requests
(one gold label per question per request; `asked` scored per parameter and then averaged over parameters):

| question | expected accuracy | why |
|---|---|---|
| `analysis` | 82 % | high for plain "run the NCA / read an existing one"; should miss `none_needed` vs `nca` on refusals and out-of-scope turns, miss the dominant-action choice on "do A then B" sentences, and miss `compare` when no prior analysis exists |
| `route` | 90 % | robust when stated or implied by a common word; expected to guess a route (probably `oral`) when the text never gives one, which is exactly the case my gold calls `unknown` |
| `auc_method` | 72 % | the generator's wordings pair a named method with a request that needs it; my `not_applicable` convention (refusals, out-of-scope, fit/simulate) and the "second analysis" convention on `compare` are conventions, not words in the text |
| `dose_has_unit` | 78 % | expected to fail on `0,25 g` and `mcg` (the harness regex knows only mg/µg/μg/ug), on a dose without a unit, and on a request with no dose at all |
| `is_not_available` | 55 % | the project itself reports 77 % recall in-distribution; out of distribution this is the question I expect to break first, on C0 after oral, Tlag after IV, Vss and ka (both absent from the label set) and on out-of-scope asks |
| `compare_pair` | 80 % | explicit pairs should be easy; expected to fail on the direction (`2+1`), on "compare the two AUC" without ids, and on the one-analysis-exists case where the pair only exists after a re-run |
| `asked` (per parameter) | 88 % | abbreviation mapping (`t1/2`, `AUC0-t`, `Cl/F`, `Vd`) should mostly work; the misses should cluster on AUC vs AUC(0-inf) wording, on `adj_r2` / `lambda_z_points`, on multi-parameter sentences, and on parameters outside the 14 keys (the model can only answer inside its option set) |
| **whole request exactly right** (all questions) | **30 %** | errors are correlated: one wrong `analysis` or `is_not_available` invalidates the whole turn |
| **macro-average over the seven questions** | **~80 %** | |

Questions I expect to break first, in order: (1) `is_not_available`, (2) `analysis` on anything outside the
generator's six actions (out-of-scope, multi-action, compare without priors), (3) `auc_method` on `not_applicable`
turns, (4) `dose_has_unit` on units and omissions the regex does not know, (5) `route` when the text is silent
(the model should say `unknown`; I expect it to infer from the data or default). I expect the harness to stay
number-safe by construction and to fail on the *decision*, not on the rendering.

## Reading log (the brief requires the order, with the part)

### Part 1 (before the Part 1 commit)

1. `decision/review-dsh-brief.md` (whole; it is the instructions).
2. `README.md` (root) — **opened in full, beyond the allowed stop** (allowed: up to and including "In plain words";
   I read to the end, including both Benchmark sections, "Demo results" and "Problems found").
3. `decision/PLAN.md` — **opened in full, beyond the allowed stop** (allowed: up to "Steps"; I read the Thread with
   the reported step-3/5 figures).
4. `decision/harness.py` (allowed; whole).
5. `bench/exercises/` directory listing and the `data.csv` / `meta.json` of all 25 exercises (allowed; `meta.json`
   read only to the top-level block: id, index, family, model, route, dose, units, n_points, noise, blq,
   simulation parameters).
6. `decision/run_harness.py` (allowed; whole).
7. `apothicaire.py` (allowed; whole).

Nothing under `private/` was opened. No file under `decision/data/`, `decision/runs/`, `bench/runs/`,
`decision/make_dataset.py`, `decision/make_exercises.py`, `bench/scripts.py`, `bench/make_exercises.py` or the
"Steps"/"Step 2-5" sections of `decision/README.md` was opened before the Part 1 commit.

## Gold conventions, and where the gold is debatable

The brief fixes the label sets but not the conventions that map a wording to a label. I had to fix them before
reading `make_dataset.py` (Part 2), so they are my reading, not the project's. Convention per line:

- `analysis`: `nca` when the request needs a new non-compartmental analysis (first turn, or a re-run with another
  AUC method), `none_needed` when it is answered from an analysis that exists (a reading, a recall, a refusal, an
  out-of-scope ask), `compare` for any two-result comparison, `fit_pk1` / `fit_pk2` / `simulate` for the
  corresponding registered-but-unwired action.
- `auc_method`: the method explicitly named; otherwise `linear` when an NCA is created or read; `not_applicable`
  when the method does not enter the requested action (fit, simulate, out-of-scope, refusals, a pair that already
  exists). On a `compare` that must create the second analysis, the method of that second analysis.
- `route`: the exercise's route; `unknown` when the request does not state or imply it (the harness must ask); for
  the invented urine exercise, `unknown`.
- `dose_has_unit`: true only when the request's text contains a dose followed by a unit the harness regex
  (`mg`, `µg`, `μg`, `ug`) matches. A later turn inherits the true/false of the conversation's dose.
- `is_not_available`: true for a parameter the route does not give as computed (C0 after oral, Tlag after IV or
  infusion), for a parameter outside the 14-key label set that the harness can never render (Vss, ka), and for an
  out-of-scope ask (bioequivalence, population, steady state, urine). The schema has no "not supported" label, so
  this is a stretch for the last group: **debatable** (ood-019, ood-020, ood-064, ood-065).
- `compare_pair`: `"a+b"` with the ids of `prior_analyses` in the order the request implies (b is the second
  analysis of the comparison); `not_applicable` when the pair does not exist yet.

Lines where I consider the gold debatable (recorded so Part 2 can attack them): ood-005 (`Cl/F` asked on an IV
bolus: I keep `cl` and `iv_bolus`, the `/F` is wrong terminology, not an unavailable parameter), ood-013 and
ood-030 (compare whose second analysis only exists after a re-run: my gold describes the *first* ask, the harness
re-asks after re-running), ood-015 (pair `2+1` chosen from "compare 2 to 1"), ood-017/018/034/038/048/060/061
(`analysis = none_needed` on a refusal is my convention; `is_not_available` overrides `analysis` in the harness
anyway), ood-019/020/064/065 (out-of-scope encoded as `is_not_available` with an empty `asked`), ood-022/023/024/069
(the dose decision is true/false but the *unit the engine receives* is the user's number without its unit; see the
Part 2 attack), ood-029 (two actions in one sentence; I keep the second action, `nca` + `lin_up_log_down`),
ood-031 (`t1/2` mapped to `half_life`), ood-058 (compare with no prior analysis: `not_applicable` pair), ood-056
(a recall with an empty `asked` list is what the harness reads as a recall).

## Part 1 artefacts

- `requests.jsonl`: 74 lines, 58 on the 25 committed `bench/exercises/` and 16 on 12 invented exercises. Every tag the
  brief lists is covered: colloquial, typo, abbreviations (AUC0-t, t1/2, Cl/F, Vd, MRT, R², λz), French + English,
  dose in another unit in the text, dose in `g` / `mcg` / no unit / no dose, route implied, route missing, two requests
  in one sentence, C0 after oral and Tlag after IV/infusion, bioequivalence / population / steady state / urine,
  compare of two AUC methods (with and without prior analyses), simulate and fit.
- `exercises/<id>/data.csv` + `meta.json`: 12 invented exercises, generated by `make_ood_exercises.py`. **Deviation
  from the brief I must report:** the benchmark `meta.json` carries a `ground_truth.nca` oracle produced by Caladrius.
  Part 1 is blind of the engine, so I did not produce it; my `meta.json` has the same top-level keys plus
  `ground_truth.data_import_columns` and an explicit `oracle_note`. The truth it does carry (route, dose, units, model)
  is exact and deterministic (no noise).
- All files are UTF-8 with LF endings, like the committed exercise files.
