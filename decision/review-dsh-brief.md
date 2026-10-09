# Brief for the independent reviewer (DeepSeek, role `contributor-dsh`, devil's advocate)

Written by the orchestrator on 2026-10-09 (night). You are not an assistant on this project: you are an independent expert whose job is to try to refute its results. Your source of truth is never our reports; it is what you can predict, reproduce or break yourself.

## Rules

- Work on a git branch `dsh/ood-requests` of this repository (`git switch -c dsh/ood-requests`). Never push. Commit your files only.
- Allowed files to create or edit: everything under `decision/ood/` and nothing else.
- English in every file you write (the requests themselves are in French, by design).
- Synthetic data only. Never read anything under a folder named `private/`.
- Order of reading matters, and you must log it. **Part 1 is written blind**: before Part 1 is committed, do not open `decision/make_dataset.py`, `decision/make_exercises.py`, `bench/scripts.py`, `bench/make_exercises.py`, `decision/data/`, `decision/runs/`, `bench/runs/`, nor the sections "Step 2" to "Step 5" of `decision/README.md`. You may read `README.md` (the root one) up to and including the section "In plain words", `decision/PLAN.md` up to the "Steps" section, `decision/harness.py`, `decision/run_harness.py`, `bench/exercises/*/meta.json` and the CSV files next to them, and `apothicaire.py`. Write in `decision/ood/REVIEW.md` the list of files you opened, in order, with the part in which you opened them.

## What the project claims (the claim you are asked to attack)

A small decision model (Qwen3.5-0.8B fine-tuned with Unsloth on about 2000 synthetic rows) answers closed questions about a pharmacokinetic request and a data table (which analysis, which route, which AUC method, does the dose carry a unit, is the asked parameter unavailable, which two analyses to compare, and one yes/no per parameter asked), and a deterministic harness then calls the Caladrius engine and writes the answer from templates. The project reports a very high per-decision accuracy on held-out synthetic exercises and a perfect score on its 25-exercise benchmark. Our own stated weakness: the held-out requests use wordings written by the same generator, so the figure is in-distribution.

## Part 1 (blind): predictions and your own requests

1. In `decision/ood/REVIEW.md`, section "Predictions", before anything else: what accuracy do you expect such a model to reach on requests written by you, per question, and which questions do you expect to break first, and why. Numbers, not adjectives.
2. Write `decision/ood/requests.jsonl`: at least 50 French requests, one JSON object per line, over the existing exercises in `bench/exercises/` (use their `meta.json` for the truth: route, dose, units, model) and at least 10 requests on exercises you invent yourself (write their CSV and a `meta.json` in the same format under `decision/ood/exercises/<id>/`). Make them hard on purpose and say how in a `tags` field: colloquial wording, typos, abbreviations (AUC0-t, t1/2, Cl/F, Vd), a different language mix (French with English terms), the dose given in the text in another unit than the data, the route implied rather than stated, two requests in one sentence, a request for a parameter that does not exist for that route (C0 after an oral dose, Tlag after IV), a request for something the engine does not do (bioequivalence, population modelling), a request with no dose, a request with the dose but no unit, a request to compare two AUC methods, a simulation or a fit request. Each line:

```json
{"id": "ood-001", "exercise": "ex02_oral_1", "turn": 1, "prior_analyses": [], "request": "...", "tags": ["typo", "unit-in-text"],
 "gold": {"analysis": "nca", "route": "oral", "auc_method": "linear", "dose_has_unit": true, "is_not_available": false,
          "compare_pair": "not_applicable", "asked": ["cmax", "tmax", "auclast"]}}
```

   `analysis` is one of `nca`, `fit_pk1`, `fit_pk2`, `simulate`, `compare`, `none_needed`; `route` one of `iv_bolus`, `iv_infusion`, `oral`, `unknown`; `auc_method` one of `linear`, `lin_up_log_down`, `not_applicable`; `asked` is the list of parameter keys the request asks for, among `cmax`, `tmax`, `auclast`, `aucinf`, `aucpext`, `lambda_z`, `lambda_z_points`, `adj_r2`, `half_life`, `cl`, `vz`, `mrt`, `c0`, `tlag`; `prior_analyses` lists the analyses already run in that conversation as `[{"id": 1, "auc_method": "linear"}]` so that a compare request can name a pair (`compare_pair` is then `"1+2"`, or `not_applicable`). Write the gold answers yourself, from the request and the exercise, and state in `REVIEW.md` any case where you think the "right" decision is debatable.
3. Commit Part 1 (`git add decision/ood && git commit`).

## Part 2: reproduce, then try to refute

4. Now read everything. Rerun what you can and compare with the reported figures: `python decision/make_dataset.py` (regenerates the dataset; the README says the result is byte-identical), `python decision/run_harness.py --decider gold-asked` (the gold ceiling on the 25 benchmark exercises; score it with `bench/score.py` as the README describes), and, if the virtual environment `.venv-unsloth` and the model folder `decision/models/qwen35-0.8b-d01/` exist, the trained-model run (`run_harness.py --help` for the decider syntax; the GPU is an RTX 3060 12 GB, nothing else should be running on it). Write the figures you obtained next to the figures reported, with the command used.
5. Attack the method, not only the numbers: is the held-out split really by exercise, do the generator's wordings leak into held-out, is the "always-majority" baseline the right baseline, does the scorer measure what the README says, what would a pharmacokineticist object to in the templates, what does the harness do on your hard requests by construction (read `harness.py` for the refusal paths). Where you can, run your own requests through the gold path by hand (the harness exposes the state builder and the templates) and report what breaks.
6. Verdict in `REVIEW.md`: what you reproduced, what you could not, what you refuted, what you would do next, ranked. Commit Part 2 on the same branch. Report in at most fifteen lines on standard output when done.
