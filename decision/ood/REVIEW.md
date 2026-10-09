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

### Part 2 (after the Part 1 commit)

8. `decision/README.md` (whole, including Steps 2-5).
9. `decision/make_dataset.py`, `bench/scripts.py`, `decision/decider_unsloth.py`.
10. `bench/score.py`, `bench/run_bench.py`.
11. `decision/predict_unsloth.py`, `decision/zero_shot_d1.py`.
12. `bench/make_exercises.py`, `decision/make_exercises.py`.
13. `decision/models/qwen35-0.8b-d01/merged/{unsloth_decision_config.json,config.json,joint_schema_model.py}` (via the
    `read` tool only; see the sandbox finding below) and `.venv-unsloth/Lib/site-packages/unsloth_zoo/hf_cache.py`.
14. `decision/data/{train,heldout,bench}.jsonl`, `decision/runs/2026-10-09-harness-qwen35-0.8b/*.json` and the
    `decision/exercises/` folders (programmatically, through the project's own loaders; no file opened by hand).

## Part 2: what I reproduced, with the command used

| claim (decision/README.md) | reported | I obtained | command |
|---|---|---|---|
| dataset regeneration is byte-identical | 1980 / 720 / 900 rows | identical SHA-256 for `train.jsonl`, `heldout.jsonl`, `bench.jsonl` **and** `decision/README.md` before/after | `python decision/make_dataset.py` |
| harness with gold decisions, `asked_<key>` (step 4b) | 175/175 turns, 558/558 numbers, 0/250 invalid calls, 0/691 gate, 1 ms/turn | **175/175, 558/558, 0/250, 0/691**, 0.001 s/turn; scorer 200/200 turns fully correct; 0 scorer/oracle disagreements; 0/75 deviating tool calls | `python decision/run_harness.py --decider gold --date 2026-10-09-dsh` (see the note) |
| trained model: 44 of 4500 answers differ from gold | 19 `is_not_available`, 25 compare first asks | **exactly 225 decide calls / 4500 answers, 19 `is_not_available` = false (all confidence < 0.86), 25 compare first asks = `not_applicable`, 0 outside options** | re-analysis of the stored `decision/runs/2026-10-09-harness-qwen35-0.8b/*.json` (no model) |
| trained harness and held-out 99.9 % | 175/175; 99.9 % | **not reproduced** (see below) | `.venv-unsloth/Scripts/python decision/run_harness.py --decider decider_unsloth:decide` |

- **The brief's command does not run:** `--decider gold-asked` raises `ModuleNotFoundError: No module named 'gold-asked'`
  (`run_harness.load_decider` accepts only `gold`); the accepted name is `gold`, and the run folder is still called
  `...-gold-asked` because the function carries `decide.name = "gold-asked"`. Trivial, but a reader copying the brief loses time.
- **The trained-model run cannot be reproduced in this session**, for two independent reasons, both recorded in
  `runs/2026-10-09-model-run-attempt-FAILED/` (25 records, 200/200 turns failed) and `runs/model_run.err`:
  1. `import unsloth` never returns while `unsloth_zoo.hf_cache` probes `~/.cache/huggingface` for writability outside
     the file sandbox (>10 min, CPU-bound, no GPU allocation; `-X importtime` stops at `numpy`). Pointing `HF_HOME`,
     `HF_HUB_CACHE` and `HF_XET_CACHE` at a writable folder inside the workspace fixes it (import in 36 s).
  2. The workspace-write sandbox denies **shell-spawned processes** read access to `decision/models/qwen35-0.8b-d01/merged/`
     and `.../adapters/` (`PermissionError: [Errno 13]`), while the harness's own `read` tool can read them and
     `.../qwen35-0.8b-d01/train_summary.json` (one level up) is readable. The one-shot escalation the sandbox offers
     (`danger-full-access`) is refused: *"requires approval, but no approval channel is available"*. The 99.9 % held-out
     and the 175/175 trained figures therefore remain **unverified by me**; `decision/ood/eval_ood_model.py` is ready to
     produce the missing out-of-distribution score in an unconfined environment.
  3. Side finding: `run_harness.py` line 171 crashes with `TypeError: unsupported format string passed to NoneType` when
     every turn failed (`mean_wall_s_per_turn` is None); the report files were written, the CLI exits 1.

## Part 2: what I attack

### The held-out split leaks the wordings (this is the big one)

The split is by exercise, and I confirm no exercise is shared (the project tests it). But the request sentences come from
one global `WORDINGS` pool in `make_dataset.py`, so:

- **720 / 720 held-out rows (100 %) use a `request` string that appears verbatim in `train.jsonl`**, and 720/720 the same
  `(kind, request)` pair; `bench.jsonl` is also 100 %. There are only **83 distinct requests** in each split
  (`runs/analyze_dataset.json`). The dose sentence differs more (46 % overlap).
- The state adds the exercise's `data.header/first_rows`, but the questions that are not `asked_*` are decided by the
  sentence and the exercise route, not by the concentration values. So "held-out" means *new data tables, same 83
  sentences*: 99.9 % measures that the generator's sentences are memorised, which is exactly the limit the project states.
  It is not evidence about a user who writes differently. My requests.jsonl is that missing test (unrun, reason above).

### "Always answer the majority" is the wrong baseline

`runs/analyze_dataset.json` (held-out, same rows):

| question | always-majority | my deterministic rule |
|---|---|---|
| route | 0.436 | **1.000** |
| analysis | 0.583 | 0.953 |
| auc_method | 0.833 | 0.972 |
| dose_has_unit | 0.818 | **1.000** |
| compare_pair | 0.917 | 0.972 |
| is_not_available | 0.917 | **0.997** |
| overall (20 questions) | 0.846 | **0.915** |

The rule is ~40 lines built from the generator's own regexes (`UNIT_RE`, `ROUTE_RE`) and the fact that `auc_method`,
`compare_pair` and `analysis` are near-deterministic functions of the turn kind (`AUC_METHOD_OF`, `ANALYSIS_OF`,
`compare_pair = ids[0]+ids[1]`). The model's margin over a rule that never sees a GPU is therefore ~8 points, not ~15;
on **`is_not_available`, the one question the project flags as weak, the model (98.1 % held-out) is *below* the rule
(99.7 %)**. The headline "majority 84.6 %" is also inflated by the 14 sparse `asked_*` booleans (mostly false); the five
real choices have majority 44-92 %. A better statement of the result would be "0.8B model ≈ hand rules on the same
template distribution". Whether the trained model beats the rules on free wording is exactly the unrun test.

### The scorer measures the answer, not the decision; 175/175 is a template test

On the decision path no generated number can exist, so the gate's 0/691 and the oracle's 558/558 are properties of
`harness.py`, not evidence about a model. The gold-decider run is a ceiling test of the templates, and it is now exact.
The scorer cannot see the two failure modes the project lists (`not_available` turns answered by the reading path score
`not_covered`; the first compare ask is unused). I verified the 19 + 25 = 44 differences are invisible to it.

### Construction bugs and refusals found by running my 74 requests through the gold path

`python decision/ood/run_ood_goldpath.py` (my gold decisions, real engine, `runs/goldpath.json`): **64/74 lines take the
branch my gold asks for**; the 10 that do not are not my gold's fault:

1. **Infusion duration parsing fails in 8/8 infusion requests** (`ood-008, 010, 011, 037, 043, 055, 062, 070` →
   `T_ASK_DURATION` although the text states the duration). `_DURATION_RE` cannot cross a digit: `parse_duration`
   returns `(None, None)` for `"Perfusion de 150 mg sur 2 h"` but `(2, "h")` for the benchmark's
   `"150 mg en perfusion intraveineuse de 2 h"` (the dose sits before the word "perfusion" there). Natural French puts
   the dose first, so the harness asks for a duration the user already gave. `"90 minutes"` fails too (`\b` after
   `min` rejects the plural); only `"90 min"` parses.
2. **`compare_pair` only offers ascending pairs:** `questions_for` builds `{f"{a}+{b}"}` with `a < b`, so "compare
   l'analyse 2 à l'analyse 1" is outside the options, is nulled by `normalize_answers`, and the harness answers
   `T_WHICH_PAIR` (`ood-015`, `ood-072`). A user cannot choose the direction of `b - a`.
3. **The refusal path names the wrong parameter.** `Harness._refuse` takes `next(iter(self.asked(a)))`, i.e. the first
   `asked_*` in `make_dataset.PARAMETERS` order, not the unavailable one. Demonstrated with the engine:
   *"Donne-moi la Cmax et la C0"* answers **"Cmax n'est pas calculé par Caladrius pour cette voie"** — Cmax *is*
   computed, C0 is not. `is_not_available` is one boolean for all parameters, so a mixed request cannot be honest.
4. **A request with no dose says the wrong thing.** `_nca` checks `dose_has_unit` before `parse_dose`, so a request with
   no dose at all gets `T_ASK_DOSE_UNIT` ("la dose n'a pas d'unité", ood-021) and `T_ASK_DOSE` ("je ne trouve pas la
   dose") is unreachable with correct decisions.
5. **Out-of-scope asks get a false claim.** Bioequivalence, population modelling, steady state and urine recovery
   (ood-019, 020, 064, 065) are answered *"Ce paramètre n'est pas calculé par Caladrius pour cette voie
   d'administration"* — there is no "not supported" label in the schema, so the schema forces a wrong explanation.
6. **The dose unit never reaches Caladrius, silently.** `ood-023` ("bolus IV de 2 mg" on the 2000 µg exercise) runs
   `nca_run(dose=2)`; the header says *"dose 2"* with no unit and CL/Vz are 1000× the meta truth in those labels. The
   decision is `dose_has_unit=true` and nothing downstream can see the unit change. Related: `render_header` prints the
   dose value without its unit at all, and the not-calculated reasons are quoted in English inside French answers.
7. **The compare turn with one analysis asks twice** (open item (b)): `ood-013/030/071` re-run the second analysis and
   re-ask; a stateless decider returns the same first answer and the harness gives `T_WHICH_PAIR`. The dataset describes
   the compare turn only after the re-run, so a model trained there may pass; my gold describes the first ask, and I say
   so.

### Calibration statement is vacuous on this task

ECE 0.001 is claimed as a result. The labels are one-hot, the task is near-deterministic and the model is at 99.9 %: no
bin can be miscalibrated. It says nothing about the ambiguous requests the dataset itself excludes, and nothing about
free wording. Reporting ECE here is not wrong but it is not evidence of trustworthiness.

## Verdict

**Reproduced (1 figure group, exact):** `make_dataset.py` byte-identical; the gold-decision harness ceiling
(175/175 turns, 558/558 numbers, 0/250 invalid calls, 0/691 gate, 0.001 s/turn, 0 scorer/oracle disagreements). I also
re-derived the reported 44/4500 trained-run decision differences from the stored run files.

**Not reproduced:** the trained Qwen3.5-0.8B runs (held-out 99.9 %, bench 175/175 trained). Two blockers: the Unsloth
import hangs on out-of-workspace HF cache probing (worked around with `HF_HOME` inside the workspace), and the sandbox
denies shell processes read access to `decision/models/.../merged/` and `/adapters/` with no approval channel available.
The model itself is therefore the one part of the claim I cannot check; the missing measurement is the OOD score, not
another benchmark run.

**Refuted / weakened:**
1. The held-out figure is a wording-memorisation figure: 100 % of held-out requests are verbatim train requests.
2. The baseline is a straw man: 40 lines of rules reach 91.5 % overall and beat the model on `is_not_available`.
3. The 175/175 (gold and trained) is a template/decision consistency test, not evidence about free wording, and the
   scorer is blind to the two failure modes the project already lists.
4. The harness is not robust to natural French: infusion duration (8/8 of my requests), compare direction, mixed
   available/unavailable parameters, out-of-scope asks, and the silently dropped dose unit.
5. ECE 0.001 is uninformative on a deterministic one-hot task.

**What I would do next, ranked:**
1. Run `decision/ood/requests.jsonl` through the trained decider in an unconfined environment
   (`decision/ood/eval_ood_model.py`, which reports both my gold and the project-convention gold). This is the single
   measurement the project says it lacks; until it exists, 99.9 % should be read as in-distribution only.
2. Hold out *wordings*, not only exercises (or freeze the wordings before the model sees any): split the 83 requests,
   keep the exercises.
3. Fix the harness first: `_DURATION_RE` (parse the duration anywhere; accept "minutes"), a directed compare pair,
   pick the unavailable parameter in `_refuse`, distinguish "no dose" from "no dose unit", and add a `not_supported`
   label/path for out-of-scope requests. The number-safety by construction survives all of these.
4. Replace the always-majority baseline with the deterministic rules in `decision/ood/analyze_dataset.py` in the
   Step 3/5 tables; report the margin over them.
5. Send the dose unit to Caladrius (a `dose_unit` argument) so CL/Vz do not depend on the user's unit token, and print
   the dose unit in `render_header`.
6. Re-run the 25 exercises with a wording-shuffled script to separate template learning from decision learning.
