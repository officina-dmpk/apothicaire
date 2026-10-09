# Training of Qwen3.5-0.8B as the D-01 decision model (step 3)

Synthetic data only. `python decision/train_unsloth.py --epochs 2 --max-seq-length 2560 --out decision/models/qwen35-0.8b-d01`
(base `unsloth/Qwen3.5-0.8B`, 4-bit, LoRA r=16 on all linear layers, batch 8 x accumulation 4, lr 2e-4 cosine, warmup 10, head lr 1e-4 by
default). Train: all 1980 rows of `decision/data/train.jsonl` (55 exercises). Evaluation and calibration: all 720 rows of `heldout.jsonl`
(20 exercises never seen in training). The 25 benchmark exercises (`bench.jsonl`) are used only for the evaluation below. Environment as in
[`../2026-10-09-smoke-unsloth/report.md`](../2026-10-09-smoke-unsloth/report.md) (torch 2.14.1+cu130, transformers 5.17.0, unsloth 2026.10.3,
RTX 3060). Model folder `decision/models/qwen35-0.8b-d01/` (adapters 113 MB, merged 1.7 GB, `train_summary.json`; git-ignored). Training
log: `train.log`.

## `build_dataset` report

| set | rows | decisions | skipped | truncated inputs (max_seq_length 2560) |
|---|---|---|---|---|
| train | 1980 | 39600 (20 per row) | 0 | **0** |
| held-out | 720 | 14400 | 0 | **0** |

`reason: None`. One item per row (a Clef model answers the 20 questions of a row in one sequence of about 2000 tokens).

## Time and memory

| step | seconds |
|---|---|
| load + LoRA | 16 |
| training, 124 optimizer steps, 2 epochs | 3237 (54 min; 20 to 25 s per step of 32 rows, first step 67 s) |
| evaluation at the end of each epoch (720 rows) | 159 and 132 |
| `calibrate` on 720 held-out rows | 142 |
| `save_pretrained` + `save_pretrained_merged` | 10.5 |
| total | 3456 (57.6 min) |

VRAM: `torch.cuda.max_memory_allocated` peak 3582 MiB during training; `nvidia-smi` peak 6123 MiB of 12288 (other processes use
about 1400 MiB of it, other processes, measured before the load). Prediction of the merged model: torch peak 1936 MiB, `nvidia-smi` 2867 MiB.

## Training curve

Mean training loss over the run 0.101. Loss every 10 steps: 0.651 (10), 0.395 (20), 0.107 (30), 0.046 (40), 0.027 (50), 0.014 (60), 0.0078 (70),
0.0026 (80), 0.0009 (90), 0.0005 (100), 0.0002 (110), 0.0003 (120). Gradient norm peaks at 2.0 (step 50), 0.01 to 0.2 after step 80. Held-out loss at
the end of epoch 1: 0.01045; at the end of epoch 2: 0.00123. `calibrate` on the 720 held-out rows (temperatures fitted by cross-fit halves):
accuracy 0.99979, ECE 0.00012, loss 0.0064, record accuracy (all 20 answers of a row right) 0.9958. The loss still falls at the end; a third epoch
would change little because the held-out accuracy is already 99.9 %.

## Evaluation (`decision/predict_unsloth.py`, cuda, merged model, one call per row = 20 questions)

```
python decision/predict_unsloth.py --model decision/models/qwen35-0.8b-d01/merged --split heldout --out-dir decision/runs/2026-10-09-train-qwen35-0.8b
python decision/predict_unsloth.py --model decision/models/qwen35-0.8b-d01/merged --split bench   --out-dir decision/runs/2026-10-09-train-qwen35-0.8b
```

Held-out: 14386 / 14400 = 99.9 %, ECE 0.0011, 175.3 ms per row (p95 178.6). Bench: 17982 / 18000 = 99.9 %, ECE 0.0011, 175.5 ms per row.
Full reports with the confusion tables: [`unsloth-qwen35-0.8b-d01-merged-heldout-cuda.md`](unsloth-qwen35-0.8b-d01-merged-heldout-cuda.md),
[`unsloth-qwen35-0.8b-d01-merged-bench-cuda.md`](unsloth-qwen35-0.8b-d01-merged-bench-cuda.md).

Accuracy per question next to the always-majority baseline (the accuracy of always giving the most frequent gold label of that question):
| question | held-out 720 rows | always-majority | bench 900 rows | always-majority |
|---|---|---|---|---|
| analysis | 100.0 % | 58.3 % | 100.0 % | 58.3 % |
| asked_adj_r2 | 100.0 % | 93.9 % | 100.0 % | 93.8 % |
| asked_aucinf | 100.0 % | 88.5 % | 100.0 % | 87.6 % |
| asked_auclast | 100.0 % | 81.5 % | 100.0 % | 81.8 % |
| asked_aucpext | 100.0 % | 93.9 % | 100.0 % | 94.2 % |
| asked_c0 | 100.0 % | 93.6 % | 100.0 % | 92.9 % |
| asked_cl | 100.0 % | 84.4 % | 100.0 % | 84.4 % |
| asked_cmax | 100.0 % | 84.0 % | 100.0 % | 84.1 % |
| asked_half_life | 100.0 % | 84.6 % | 100.0 % | 84.3 % |
| asked_lambda_z | 100.0 % | 90.0 % | 100.0 % | 90.2 % |
| asked_lambda_z_points | 100.0 % | 92.9 % | 100.0 % | 93.0 % |
| asked_mrt | 100.0 % | 88.3 % | 100.0 % | 88.7 % |
| asked_tlag | 100.0 % | 96.1 % | 100.0 % | 96.9 % |
| asked_tmax | 100.0 % | 84.4 % | 100.0 % | 84.4 % |
| asked_vz | 100.0 % | 85.1 % | 100.0 % | 84.8 % |
| auc_method | 100.0 % | 83.3 % | 100.0 % | 83.3 % |
| compare_pair | 100.0 % | 91.7 % | 100.0 % | 91.7 % |
| dose_has_unit | 100.0 % | 81.8 % | 100.0 % | 84.0 % |
| is_not_available | 98.1 % | 91.7 % | 98.0 % | 91.7 % |
| route | 100.0 % | 43.6 % | 100.0 % | 49.8 % |
| **overall** | 99.9 % | 84.6 % | 99.9 % | 85.0 % |

**No question is at or below its majority baseline.** The smallest margin is `is_not_available` (98.1 % / 98.0 % against 91.7 %): see below.
Every other question is at 100.0 % (the 14 and 18 errors of the whole evaluation are all `is_not_available`).

Confusion summaries (rows = gold, columns = predicted; only the non-zero cells are listed; the full tables are in the two reports above):

| question | held-out | bench |
|---|---|---|
| `analysis` (6 classes) | diagonal only (nca 60, fit_pk1 60, fit_pk2 60, simulate 60, compare 60, none_needed 420) | diagonal only (75 x 5, none_needed 525) |
| `route` (4 classes) | diagonal only (iv_bolus 231, iv_infusion 89, oral 314, unknown 86) | diagonal only (241, 95, 448, 116) |
| `auc_method` | diagonal only (linear 60, lin_up_log_down 60, not_applicable 600) | diagonal only (75, 75, 750) |
| `compare_pair` | diagonal only (2+3: 60, not_applicable 660) | diagonal only (75, 825) |
| `is_not_available` | false: 659 right, **1** predicted true; true: 47 right, **13** predicted false (recall 78.3 %) | false: 824 right, 1 predicted true; true: 58 right, **17** predicted false (recall 77.3 %) |

All 13 + 17 misses of the true class are rows of the `not_available` turn kind (Tlag or C0 asked for a route that does not compute it); the
two false alarms (one per set) are on `cmax_tmax` rows. The model reads the parameter but not always the route/parameter rule behind it.

Calibration (10 bins of the probability of the chosen label, all questions; held-out, bench has the same shape): ECE 0.0011. 14326 of 14400
answers (99.5 %) are in the top bin with 100.0 % observed accuracy. The 74 answers below 0.9 are all in 0.5 to 0.9 (mean predicted / observed
0.554 / 0.643 (14), 0.649 / 0.533 (15), 0.763 / 1.000 (17), 0.850 / 0.929 (28)); 64 of them are `is_not_available` answers, 7 `analysis`, 2 `auc_method`, 1 `dose_has_unit`. The bins
below 0.5 are empty because every question here has a clear winner. The reliability of the mid bins rests on 14 to 28 answers each.

## Reading the result with care

- **The 99.9 % is within the distribution of the generator, not a measure of free French.** Held-out exercises are new in numbers (new
  data, doses, units, routes) but the sentences come from the same 4 to 5 hand-written wordings per kind (`WORDINGS`) and the same 5 data
  introductions, so the model has seen each wording on other exercises. The held-out set tests generalisation across exercises, not across
  wordings. A test with sentences written by someone else (a friend, the human) is the missing measure.
- The bench set is in the same distribution: its exercises are excluded from train, and its scripted wordings are the same sentences as in
  the benchmark scripts, which the paraphrases of train are modelled on.
- `is_not_available` is the only question with errors. The harness does not depend on it for correctness (see the Step 5 section of
  `decision/README.md`: on a miss, it reads the analysis and says what Caladrius says).
- Proposal, not done: `is_not_available` is the rarest class (8.3 % true). One concrete next step is a class weight on the `true` side of that
  question (or 2x more `not_available` exercises, 55 train exercises give 165 true rows) and a re-train of 55 min; the alternative is to drop
  the question and let the harness derive the refusal from the engine's `not_calculated` list, which it already consults.