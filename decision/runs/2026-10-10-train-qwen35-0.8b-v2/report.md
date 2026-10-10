# Step 7: Qwen3.5-0.8B trained on dataset v2 (wording-level split) and the relevance ablation

Synthetic data only; run of 2026-10-10 on the RTX 3060 (12 GB), no other process on the GPU. Everything below is produced by code of this repository
(`train_unsloth.py`, `predict_unsloth.py`, `eval_ood.py`, `run_harness.py`, `ablation.py`, `set_tables.py`); raw files are in this folder.

**Two forms of the same trained model are scored everywhere.** *v2 merged* is the 16-bit file `decision/models/qwen35-0.8b-d01-v2/merged` that `save_pretrained_merged`
writes and that Steps 3, 5 and 6 measured (the default of `decider_unsloth.py`); *v2 adapters* is `.../adapters` (LoRA + head) loaded on the 4-bit base, which is the model as
it was trained and calibrated. They are not the same model in practice (section 3). Training: `python decision/train_unsloth.py --base <local snapshot of unsloth/Qwen3.5-0.8B>
--train train --heldout heldout_exercises --epochs 2 --max-seq-length 2560 --out decision/models/qwen35-0.8b-d01-v2` (the base was given as the folder of the local Hugging Face
cache snapshot, so that the fresh `HF_HOME` / `HF_HUB_CACHE` / `HF_XET_CACHE` of the README's `import unsloth` workaround, with `HF_HUB_OFFLINE=1`, needed no download).

## 1. Data

`python decision/make_dataset.py --no-readme` (3 s): train 2530 rows (55 exercises, 166 wordings), heldout_exercises 920 (20 exercises), heldout_wordings 825 (55 exercises, 52 held-out
wordings), heldout_both 593 (20 exercises, 52 held-out wordings), bench 1150 (the 25 benchmark exercises). `python decision/eval_ood.py --convert-only`: **74 lines converted, 0 rejected**
(`decision/ood/schema_report.md`, regenerated: gold `compare_pair` is now `2+3` x2, `3+2` x2, `not_applicable` x70; the 22 warnings are the same as before). `heldout_wordings`, `heldout_both`
and `bench` were not used for training, for the evaluation passes of the trainer nor for calibration: only `train` (training) and `heldout_exercises` (end-of-epoch loss and `calibrate`).

## 2. Training

| item | value |
|---|---|
| `build_dataset` | train: 50600 decisions (2530 rows x 20), **0 skipped, 0 truncated**; held-out: 18400 decisions, 0 skipped, 0 truncated (`max_seq_length` 2560) |
| steps | 160 (2 epochs, batch 8 x accumulation 4), 21.0 s per step after the first |
| wall time | training 3831 s (63.9 min); load + LoRA 10 s; `calibrate` on the 920 rows 184 s; save 9 s; **total 4089 s (68.2 min)** |
| VRAM | torch peak allocated **3674 MiB**; `nvidia-smi` peak **5201 MiB** of 12288 (833 MiB used before the load) |
| training loss | mean over the run 0.1038; every 20 steps: 0.468 (20), 0.110 (40), 0.053 (60), 0.0153 (80), 0.0086 (100), 0.0035 (120), 0.0026 (140), 0.0021 (160); gradient norm at most 1.20 (first steps) |
| held-out loss (`heldout_exercises`) | 0.01269 after epoch 1, 0.00143 after epoch 2 (v1: 0.01045 and 0.00123 on 720 rows) |
| `calibrate` (`heldout_exercises`, in memory, 4-bit model) | accuracy 0.99984, ECE 0.0002, loss 0.0008, **record accuracy 0.9967** |

`train_summary.json` (versions, args, log history) and `train.log` are in this folder. Environment: torch 2.14.1+cu130, transformers 5.17.0, unsloth 2026.10.3.

## 3. The merged file is not the trained model (found while evaluating)

`predict_unsloth.py` on `heldout_exercises` with the merged file gave 99.5 % per decision and 90.0 % complete vectors, whereas the trainer's own `calibrate` on the same 920 rows said 99.984 %
and record accuracy 0.9967. The adapters on the 4-bit base reproduce `calibrate` exactly (917 / 920 complete vectors = 0.99674; 18397 / 18400 decisions). The difference sits in one question:
`is_not_available` with the merged file answers `false` on every row with P(true) of about 0.0 (recall of the true class **0 / 60** on `heldout_exercises`, 0 / 75 on bench), with the adapters
60 / 60 and 74 / 75. Other questions lose a few points too (`analysis` 99.1 % against 100.0 %, `auc_method` 98.4 % against 99.7 %). The cause was not isolated (a loss of the LoRA
delta when it is added to the dequantised 4-bit weights and rounded to 16 bit is the usual suspect; nothing here tests it). The v1 merged file shows the same signature (its `calibrate` record accuracy 0.9958
against 706 / 720 = 98.1 % complete vectors by `predict_unsloth.py`). Consequence: every merged-file figure of Steps 3, 5 and 6 understates the trained model in distribution, most on
`is_not_available`; on the reviewer's 74 requests the two forms are close (v1: 4 / 74 merged, 6 / 74 adapters, same failures), so the verdict of Step 6 does not depend on it.
Extra diagnostic run on every fourth row of `heldout_exercises` (230 rows): [`diag-adapters-4bit/`](diag-adapters-4bit/) 4599 / 4600.

## 4. The four sets

Accuracy per question (v2 columns are on the same rows; "best constant" is chosen with the gold of these rows; "reviewer's rules" = `ood/rules_decider.py`, `asked_<parameter>` always false;
v1 columns are the v1 model on its own, older files: 720 and 900 rows, 6 `analysis` options, no `not_supported`, so only comparable as an order of magnitude; v1 never saw the wording-level sets).
"All 20 right on a row" is the complete-vector accuracy. Confusion tables for `analysis`, `route`, `auc_method`, `compare_pair`, `is_not_available` and the calibration table
follow each table (the full reports, with the 20-question tables, are `unsloth-qwen35-0.8b-d01-v2-{merged,adapters}-<set>-cuda.md` and `tables-*.md`). Mean time per row:
178 ms merged, 207 ms adapters (RTX 3060, one call per row, 20 questions).

### heldout_exercises (920 rows)

| question | v1 held-out (720 rows, old file) | v2 merged (16-bit file) | v2 adapters (4-bit, as trained) | best constant | reviewer's rules |
|---|---|---|---|---|---|
| analysis | 100.0 % | 99.1 % | 100.0 % | 45.7 % | 76.7 % |
| route | 100.0 % | 100.0 % | 100.0 % | 44.3 % | 82.3 % |
| auc_method | 100.0 % | 98.4 % | 99.7 % | 78.3 % | 80.5 % |
| dose_has_unit | 100.0 % | 99.6 % | 100.0 % | 81.4 % | 89.7 % |
| is_not_available | 98.1 % | 93.5 % | 100.0 % | 93.5 % | 97.9 % |
| compare_pair | 100.0 % | 99.2 % | 100.0 % | 87.0 % | 91.8 % |
| `asked_<parameter>` (14 pooled) | 100.0 % | 100.0 % | 100.0 % | 91.0 % | 91.0 % |
| macro-average of the seven | 99.7 % | 98.5 % | 100.0 % | 74.4 % | 87.1 % |
| **all 20, per decision** | 99.9 % | 99.5 % | 100.0 % | 85.2 % | 89.7 % |
| **all 20 right on a row** | 706 / 720 | 828 / 920 | 917 / 920 | n/a | 98 / 920 |

Confusions, v2 adapters:

Confusion `analysis` (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | not_supported | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|---|
| compare | 120 |  |  |  |  |  |  | 120 | 100.0 % |
| fit_pk1 |  | 60 |  |  |  |  |  | 60 | 100.0 % |
| fit_pk2 |  |  | 60 |  |  |  |  | 60 | 100.0 % |
| nca |  |  |  | 140 |  |  |  | 140 | 100.0 % |
| none_needed |  |  |  |  | 420 |  |  | 420 | 100.0 % |
| not_supported |  |  |  |  |  | 60 |  | 60 | 100.0 % |
| simulate |  |  |  |  |  |  | 60 | 60 | 100.0 % |

Confusion `route` (rows = gold, columns = predicted)

| gold \ pred | iv_bolus | iv_infusion | oral | unknown | total | recall |
|---|---|---|---|---|---|---|
| iv_bolus | 285 |  |  |  | 285 | 100.0 % |
| iv_infusion |  | 118 |  |  | 118 | 100.0 % |
| oral |  |  | 408 |  | 408 | 100.0 % |
| unknown |  |  |  | 109 | 109 | 100.0 % |

Confusion `auc_method` (rows = gold, columns = predicted)

| gold \ pred | lin_up_log_down | linear | not_applicable | total | recall |
|---|---|---|---|---|---|
| lin_up_log_down | 75 |  |  | 75 | 100.0 % |
| linear |  | 122 | 3 | 125 | 97.6 % |
| not_applicable |  |  | 720 | 720 | 100.0 % |

Confusion `compare_pair` (rows = gold, columns = predicted)

| gold \ pred | 2+3 | 3+2 | not_applicable | total | recall |
|---|---|---|---|---|---|
| 2+3 | 89 |  |  | 89 | 100.0 % |
| 3+2 |  | 31 |  | 31 | 100.0 % |
| not_applicable |  |  | 800 | 800 | 100.0 % |

Confusion `is_not_available` (rows = gold, columns = predicted)

| gold \ pred | false | true | total | recall |
|---|---|---|---|---|
| false | 860 |  | 860 | 100.0 % |
| true |  | 60 | 60 | 100.0 % |

Calibration, v2 adapters (all questions; ECE 0.000):

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 0 | - | - |
| [0.3, 0.4) | 0 | - | - |
| [0.4, 0.5) | 0 | - | - |
| [0.5, 0.6) | 1 | 0.566 | 1.000 |
| [0.6, 0.7) | 1 | 0.626 | 1.000 |
| [0.7, 0.8) | 2 | 0.752 | 1.000 |
| [0.8, 0.9) | 10 | 0.859 | 1.000 |
| [0.9, 1.0] | 18386 | 1.000 | 1.000 |

Confusions, v2 merged:

Confusion `analysis` (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | not_supported | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|---|
| compare | 120 |  |  |  |  |  |  | 120 | 100.0 % |
| fit_pk1 |  | 55 |  |  | 5 |  |  | 60 | 91.7 % |
| fit_pk2 |  |  | 60 |  |  |  |  | 60 | 100.0 % |
| nca |  |  |  | 140 |  |  |  | 140 | 100.0 % |
| none_needed |  |  |  |  | 420 |  |  | 420 | 100.0 % |
| not_supported |  |  |  | 2 | 1 | 57 |  | 60 | 95.0 % |
| simulate |  |  |  |  |  |  | 60 | 60 | 100.0 % |

Confusion `route` (rows = gold, columns = predicted)

| gold \ pred | iv_bolus | iv_infusion | oral | unknown | total | recall |
|---|---|---|---|---|---|---|
| iv_bolus | 285 |  |  |  | 285 | 100.0 % |
| iv_infusion |  | 118 |  |  | 118 | 100.0 % |
| oral |  |  | 408 |  | 408 | 100.0 % |
| unknown |  |  |  | 109 | 109 | 100.0 % |

Confusion `auc_method` (rows = gold, columns = predicted)

| gold \ pred | lin_up_log_down | linear | not_applicable | total | recall |
|---|---|---|---|---|---|
| lin_up_log_down | 75 |  |  | 75 | 100.0 % |
| linear |  | 114 | 11 | 125 | 91.2 % |
| not_applicable | 4 |  | 716 | 720 | 99.4 % |

Confusion `compare_pair` (rows = gold, columns = predicted)

| gold \ pred | 2+3 | 3+2 | not_applicable | total | recall |
|---|---|---|---|---|---|
| 2+3 | 89 |  |  | 89 | 100.0 % |
| 3+2 | 7 | 24 |  | 31 | 77.4 % |
| not_applicable |  |  | 800 | 800 | 100.0 % |

Confusion `is_not_available` (rows = gold, columns = predicted)

| gold \ pred | false | true | total | recall |
|---|---|---|---|---|
| false | 860 |  | 860 | 100.0 % |
| true | 60 |  | 60 | 0.0 % |

Calibration, v2 merged (all questions; ECE 0.004):

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 0 | - | - |
| [0.3, 0.4) | 0 | - | - |
| [0.4, 0.5) | 0 | - | - |
| [0.5, 0.6) | 10 | 0.563 | 0.600 |
| [0.6, 0.7) | 11 | 0.657 | 0.636 |
| [0.7, 0.8) | 17 | 0.759 | 0.765 |
| [0.8, 0.9) | 35 | 0.856 | 0.800 |
| [0.9, 1.0] | 18327 | 1.000 | 0.996 |

### heldout_wordings (825 rows)

| question | v2 merged (16-bit file) | v2 adapters (4-bit, as trained) | best constant | reviewer's rules |
|---|---|---|---|---|
| analysis | 94.5 % | 95.2 % | 46.7 % | 77.0 % |
| route | 99.5 % | 99.5 % | 49.2 % | 30.9 % |
| auc_method | 90.4 % | 91.5 % | 80.0 % | 84.7 % |
| dose_has_unit | 100.0 % | 100.0 % | 79.2 % | 88.0 % |
| is_not_available | 93.3 % | 95.8 % | 93.3 % | 94.9 % |
| compare_pair | 97.3 % | 98.5 % | 86.7 % | 95.5 % |
| `asked_<parameter>` (14 pooled) | 98.7 % | 98.9 % | 91.3 % | 91.3 % |
| macro-average of the seven | 96.3 % | 97.0 % | 75.2 % | 80.3 % |
| **all 20, per decision** | 97.9 % | 98.2 % | 85.6 % | 87.4 % |
| **all 20 right on a row** | 520 / 825 | 568 / 825 | n/a | 22 / 825 |

Confusions, v2 adapters:

Confusion `analysis` (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | not_supported | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|---|
| compare | 110 |  |  |  |  |  |  | 110 | 100.0 % |
| fit_pk1 |  | 55 |  |  |  |  |  | 55 | 100.0 % |
| fit_pk2 |  |  | 36 | 1 | 18 |  |  | 55 | 65.5 % |
| nca |  |  |  | 100 | 10 |  |  | 110 | 90.9 % |
| none_needed |  |  |  | 1 | 380 | 4 |  | 385 | 98.7 % |
| not_supported |  |  |  |  | 6 | 49 |  | 55 | 89.1 % |
| simulate |  |  |  |  |  |  | 55 | 55 | 100.0 % |

Confusion `route` (rows = gold, columns = predicted)

| gold \ pred | iv_bolus | iv_infusion | oral | unknown | total | recall |
|---|---|---|---|---|---|---|
| iv_bolus | 214 |  |  |  | 214 | 100.0 % |
| iv_infusion |  | 72 |  | 4 | 76 | 94.7 % |
| oral |  |  | 406 |  | 406 | 100.0 % |
| unknown |  |  |  | 129 | 129 | 100.0 % |

Confusion `auc_method` (rows = gold, columns = predicted)

| gold \ pred | lin_up_log_down | linear | not_applicable | total | recall |
|---|---|---|---|---|---|
| lin_up_log_down | 50 |  | 5 | 55 | 90.9 % |
| linear | 2 | 75 | 33 | 110 | 68.2 % |
| not_applicable | 22 | 8 | 630 | 660 | 95.5 % |

Confusion `compare_pair` (rows = gold, columns = predicted)

| gold \ pred | 2+3 | 3+2 | not_applicable | total | recall |
|---|---|---|---|---|---|
| 2+3 | 79 |  |  | 79 | 100.0 % |
| 3+2 | 12 | 19 |  | 31 | 61.3 % |
| not_applicable |  |  | 715 | 715 | 100.0 % |

Confusion `is_not_available` (rows = gold, columns = predicted)

| gold \ pred | false | true | total | recall |
|---|---|---|---|---|
| false | 770 |  | 770 | 100.0 % |
| true | 35 | 20 | 55 | 36.4 % |

Calibration, v2 adapters (all questions; ECE 0.016):

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 0 | - | - |
| [0.3, 0.4) | 1 | 0.339 | 0.000 |
| [0.4, 0.5) | 5 | 0.455 | 0.800 |
| [0.5, 0.6) | 16 | 0.540 | 0.438 |
| [0.6, 0.7) | 20 | 0.662 | 0.300 |
| [0.7, 0.8) | 24 | 0.744 | 0.417 |
| [0.8, 0.9) | 39 | 0.843 | 0.590 |
| [0.9, 1.0] | 16395 | 1.000 | 0.985 |

Confusions, v2 merged:

Confusion `analysis` (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | not_supported | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|---|
| compare | 110 |  |  |  |  |  |  | 110 | 100.0 % |
| fit_pk1 |  | 55 |  |  |  |  |  | 55 | 100.0 % |
| fit_pk2 |  |  | 39 | 1 | 15 |  |  | 55 | 70.9 % |
| nca |  |  |  | 97 | 13 |  |  | 110 | 88.2 % |
| none_needed |  |  |  | 4 | 381 |  |  | 385 | 99.0 % |
| not_supported |  |  |  |  | 12 | 43 |  | 55 | 78.2 % |
| simulate |  |  |  |  |  |  | 55 | 55 | 100.0 % |

Confusion `route` (rows = gold, columns = predicted)

| gold \ pred | iv_bolus | iv_infusion | oral | unknown | total | recall |
|---|---|---|---|---|---|---|
| iv_bolus | 213 | 1 |  |  | 214 | 99.5 % |
| iv_infusion | 1 | 73 |  | 2 | 76 | 96.1 % |
| oral |  |  | 406 |  | 406 | 100.0 % |
| unknown |  |  |  | 129 | 129 | 100.0 % |

Confusion `auc_method` (rows = gold, columns = predicted)

| gold \ pred | lin_up_log_down | linear | not_applicable | total | recall |
|---|---|---|---|---|---|
| lin_up_log_down | 54 |  | 1 | 55 | 98.2 % |
| linear |  | 54 | 56 | 110 | 49.1 % |
| not_applicable | 22 |  | 638 | 660 | 96.7 % |

Confusion `compare_pair` (rows = gold, columns = predicted)

| gold \ pred | 2+3 | 3+2 | not_applicable | total | recall |
|---|---|---|---|---|---|
| 2+3 | 79 |  |  | 79 | 100.0 % |
| 3+2 | 22 | 9 |  | 31 | 29.0 % |
| not_applicable |  |  | 715 | 715 | 100.0 % |

Confusion `is_not_available` (rows = gold, columns = predicted)

| gold \ pred | false | true | total | recall |
|---|---|---|---|---|
| false | 770 |  | 770 | 100.0 % |
| true | 55 |  | 55 | 0.0 % |

Calibration, v2 merged (all questions; ECE 0.019):

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 0 | - | - |
| [0.3, 0.4) | 0 | - | - |
| [0.4, 0.5) | 0 | - | - |
| [0.5, 0.6) | 22 | 0.547 | 0.636 |
| [0.6, 0.7) | 18 | 0.659 | 0.278 |
| [0.7, 0.8) | 30 | 0.760 | 0.433 |
| [0.8, 0.9) | 44 | 0.856 | 0.705 |
| [0.9, 1.0] | 16386 | 1.000 | 0.982 |

### heldout_both (593 rows)

| question | v2 merged (16-bit file) | v2 adapters (4-bit, as trained) | best constant | reviewer's rules |
|---|---|---|---|---|
| analysis | 95.3 % | 95.1 % | 46.0 % | 78.6 % |
| route | 98.3 % | 99.2 % | 41.5 % | 40.3 % |
| auc_method | 88.0 % | 90.7 % | 79.8 % | 85.7 % |
| dose_has_unit | 100.0 % | 100.0 % | 78.4 % | 90.1 % |
| is_not_available | 94.4 % | 96.3 % | 94.4 % | 95.3 % |
| compare_pair | 97.0 % | 98.0 % | 86.5 % | 94.9 % |
| `asked_<parameter>` (14 pooled) | 98.8 % | 98.9 % | 91.7 % | 91.7 % |
| macro-average of the seven | 96.0 % | 96.9 % | 74.1 % | 82.4 % |
| **all 20, per decision** | 97.8 % | 98.2 % | 85.6 % | 88.5 % |
| **all 20 right on a row** | 362 / 593 | 400 / 593 | n/a | 33 / 593 |

Confusions, v2 adapters:

Confusion `analysis` (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | not_supported | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|---|
| compare | 80 |  |  |  |  |  |  | 80 | 100.0 % |
| fit_pk1 |  | 40 |  |  |  |  |  | 40 | 100.0 % |
| fit_pk2 |  |  | 22 | 2 | 14 | 2 |  | 40 | 55.0 % |
| nca |  |  |  | 75 | 5 |  |  | 80 | 93.8 % |
| none_needed |  |  |  | 1 | 272 |  |  | 273 | 99.6 % |
| not_supported |  |  |  |  | 5 | 35 |  | 40 | 87.5 % |
| simulate |  |  |  |  |  |  | 40 | 40 | 100.0 % |

Confusion `route` (rows = gold, columns = predicted)

| gold \ pred | iv_bolus | iv_infusion | oral | unknown | total | recall |
|---|---|---|---|---|---|---|
| iv_bolus | 157 |  |  |  | 157 | 100.0 % |
| iv_infusion |  | 66 |  | 5 | 71 | 93.0 % |
| oral |  |  | 246 |  | 246 | 100.0 % |
| unknown |  |  |  | 119 | 119 | 100.0 % |

Confusion `auc_method` (rows = gold, columns = predicted)

| gold \ pred | lin_up_log_down | linear | not_applicable | total | recall |
|---|---|---|---|---|---|
| lin_up_log_down | 37 |  | 3 | 40 | 92.5 % |
| linear | 3 | 51 | 26 | 80 | 63.8 % |
| not_applicable | 18 | 5 | 450 | 473 | 95.1 % |

Confusion `compare_pair` (rows = gold, columns = predicted)

| gold \ pred | 2+3 | 3+2 | not_applicable | total | recall |
|---|---|---|---|---|---|
| 2+3 | 55 |  |  | 55 | 100.0 % |
| 3+2 | 12 | 13 |  | 25 | 52.0 % |
| not_applicable |  |  | 513 | 513 | 100.0 % |

Confusion `is_not_available` (rows = gold, columns = predicted)

| gold \ pred | false | true | total | recall |
|---|---|---|---|---|
| false | 560 |  | 560 | 100.0 % |
| true | 22 | 11 | 33 | 33.3 % |

Calibration, v2 adapters (all questions; ECE 0.016):

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 0 | - | - |
| [0.3, 0.4) | 1 | 0.315 | 0.000 |
| [0.4, 0.5) | 2 | 0.470 | 0.500 |
| [0.5, 0.6) | 12 | 0.549 | 0.333 |
| [0.6, 0.7) | 22 | 0.641 | 0.455 |
| [0.7, 0.8) | 14 | 0.755 | 0.286 |
| [0.8, 0.9) | 23 | 0.854 | 0.522 |
| [0.9, 1.0] | 11786 | 1.000 | 0.985 |

Confusions, v2 merged:

Confusion `analysis` (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | not_supported | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|---|
| compare | 80 |  |  |  |  |  |  | 80 | 100.0 % |
| fit_pk1 |  | 40 |  |  |  |  |  | 40 | 100.0 % |
| fit_pk2 |  |  | 29 |  | 11 |  |  | 40 | 72.5 % |
| nca |  |  |  | 73 | 7 |  |  | 80 | 91.2 % |
| none_needed |  |  |  | 2 | 271 |  |  | 273 | 99.3 % |
| not_supported |  |  |  |  | 8 | 32 |  | 40 | 80.0 % |
| simulate |  |  |  |  |  |  | 40 | 40 | 100.0 % |

Confusion `route` (rows = gold, columns = predicted)

| gold \ pred | iv_bolus | iv_infusion | oral | unknown | total | recall |
|---|---|---|---|---|---|---|
| iv_bolus | 157 |  |  |  | 157 | 100.0 % |
| iv_infusion | 7 | 61 |  | 3 | 71 | 85.9 % |
| oral |  |  | 246 |  | 246 | 100.0 % |
| unknown |  |  |  | 119 | 119 | 100.0 % |

Confusion `auc_method` (rows = gold, columns = predicted)

| gold \ pred | lin_up_log_down | linear | not_applicable | total | recall |
|---|---|---|---|---|---|
| lin_up_log_down | 40 |  |  | 40 | 100.0 % |
| linear |  | 27 | 53 | 80 | 33.8 % |
| not_applicable | 18 |  | 455 | 473 | 96.2 % |

Confusion `compare_pair` (rows = gold, columns = predicted)

| gold \ pred | 2+3 | 3+2 | not_applicable | total | recall |
|---|---|---|---|---|---|
| 2+3 | 55 |  |  | 55 | 100.0 % |
| 3+2 | 18 | 7 |  | 25 | 28.0 % |
| not_applicable |  |  | 513 | 513 | 100.0 % |

Confusion `is_not_available` (rows = gold, columns = predicted)

| gold \ pred | false | true | total | recall |
|---|---|---|---|---|
| false | 560 |  | 560 | 100.0 % |
| true | 33 |  | 33 | 0.0 % |

Calibration, v2 merged (all questions; ECE 0.020):

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 0 | - | - |
| [0.3, 0.4) | 0 | - | - |
| [0.4, 0.5) | 1 | 0.439 | 1.000 |
| [0.5, 0.6) | 21 | 0.554 | 0.571 |
| [0.6, 0.7) | 6 | 0.643 | 0.667 |
| [0.7, 0.8) | 28 | 0.758 | 0.250 |
| [0.8, 0.9) | 41 | 0.853 | 0.707 |
| [0.9, 1.0] | 11763 | 1.000 | 0.982 |

### bench (1150 rows)

| question | v1 bench (900 rows, old file) | v2 merged (16-bit file) | v2 adapters (4-bit, as trained) | best constant | reviewer's rules |
|---|---|---|---|---|---|
| analysis | 100.0 % | 98.8 % | 100.0 % | 45.7 % | 76.1 % |
| route | 100.0 % | 100.0 % | 100.0 % | 47.6 % | 82.3 % |
| auc_method | 100.0 % | 98.2 % | 99.4 % | 78.3 % | 79.8 % |
| dose_has_unit | 100.0 % | 99.7 % | 100.0 % | 82.0 % | 88.8 % |
| is_not_available | 98.0 % | 93.5 % | 99.9 % | 93.5 % | 97.5 % |
| compare_pair | 100.0 % | 99.4 % | 100.0 % | 87.0 % | 92.3 % |
| `asked_<parameter>` (14 pooled) | 100.0 % | 100.0 % | 100.0 % | 90.9 % | 90.9 % |
| macro-average of the seven | 99.7 % | 98.5 % | 99.9 % | 75.0 % | 86.8 % |
| **all 20, per decision** | 99.9 % | 99.5 % | 100.0 % | 85.3 % | 89.5 % |
| **all 20 right on a row** | 882 / 900 | 1031 / 1150 | 1142 / 1150 | n/a | 127 / 1150 |

Confusions, v2 adapters:

Confusion `analysis` (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | not_supported | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|---|
| compare | 150 |  |  |  |  |  |  | 150 | 100.0 % |
| fit_pk1 |  | 75 |  |  |  |  |  | 75 | 100.0 % |
| fit_pk2 |  |  | 75 |  |  |  |  | 75 | 100.0 % |
| nca |  |  |  | 175 |  |  |  | 175 | 100.0 % |
| none_needed |  |  |  |  | 525 |  |  | 525 | 100.0 % |
| not_supported |  |  |  |  |  | 75 |  | 75 | 100.0 % |
| simulate |  |  |  |  |  |  | 75 | 75 | 100.0 % |

Confusion `route` (rows = gold, columns = predicted)

| gold \ pred | iv_bolus | iv_infusion | oral | unknown | total | recall |
|---|---|---|---|---|---|---|
| iv_bolus | 313 |  |  |  | 313 | 100.0 % |
| iv_infusion |  | 117 |  |  | 117 | 100.0 % |
| oral |  |  | 547 |  | 547 | 100.0 % |
| unknown |  |  |  | 173 | 173 | 100.0 % |

Confusion `auc_method` (rows = gold, columns = predicted)

| gold \ pred | lin_up_log_down | linear | not_applicable | total | recall |
|---|---|---|---|---|---|
| lin_up_log_down | 94 |  |  | 94 | 100.0 % |
| linear |  | 149 | 7 | 156 | 95.5 % |
| not_applicable |  |  | 900 | 900 | 100.0 % |

Confusion `compare_pair` (rows = gold, columns = predicted)

| gold \ pred | 2+3 | 3+2 | not_applicable | total | recall |
|---|---|---|---|---|---|
| 2+3 | 113 |  |  | 113 | 100.0 % |
| 3+2 |  | 37 |  | 37 | 100.0 % |
| not_applicable |  |  | 1000 | 1000 | 100.0 % |

Confusion `is_not_available` (rows = gold, columns = predicted)

| gold \ pred | false | true | total | recall |
|---|---|---|---|---|
| false | 1075 |  | 1075 | 100.0 % |
| true | 1 | 74 | 75 | 98.7 % |

Calibration, v2 adapters (all questions; ECE 0.000):

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 0 | - | - |
| [0.3, 0.4) | 0 | - | - |
| [0.4, 0.5) | 0 | - | - |
| [0.5, 0.6) | 1 | 0.589 | 0.000 |
| [0.6, 0.7) | 3 | 0.650 | 0.667 |
| [0.7, 0.8) | 8 | 0.768 | 0.875 |
| [0.8, 0.9) | 13 | 0.850 | 0.846 |
| [0.9, 1.0] | 22975 | 1.000 | 1.000 |

Confusions, v2 merged:

Confusion `analysis` (rows = gold, columns = predicted)

| gold \ pred | compare | fit_pk1 | fit_pk2 | nca | none_needed | not_supported | simulate | total | recall |
|---|---|---|---|---|---|---|---|---|---|
| compare | 150 |  |  |  |  |  |  | 150 | 100.0 % |
| fit_pk1 |  | 68 |  | 2 | 5 |  |  | 75 | 90.7 % |
| fit_pk2 |  |  | 75 |  |  |  |  | 75 | 100.0 % |
| nca |  |  |  | 174 | 1 |  |  | 175 | 99.4 % |
| none_needed |  |  |  |  | 525 |  |  | 525 | 100.0 % |
| not_supported |  |  |  | 2 | 4 | 69 |  | 75 | 92.0 % |
| simulate |  |  |  |  |  |  | 75 | 75 | 100.0 % |

Confusion `route` (rows = gold, columns = predicted)

| gold \ pred | iv_bolus | iv_infusion | oral | unknown | total | recall |
|---|---|---|---|---|---|---|
| iv_bolus | 313 |  |  |  | 313 | 100.0 % |
| iv_infusion |  | 117 |  |  | 117 | 100.0 % |
| oral |  |  | 547 |  | 547 | 100.0 % |
| unknown |  |  |  | 173 | 173 | 100.0 % |

Confusion `auc_method` (rows = gold, columns = predicted)

| gold \ pred | lin_up_log_down | linear | not_applicable | total | recall |
|---|---|---|---|---|---|
| lin_up_log_down | 94 |  |  | 94 | 100.0 % |
| linear |  | 142 | 14 | 156 | 91.0 % |
| not_applicable | 7 |  | 893 | 900 | 99.2 % |

Confusion `compare_pair` (rows = gold, columns = predicted)

| gold \ pred | 2+3 | 3+2 | not_applicable | total | recall |
|---|---|---|---|---|---|
| 2+3 | 113 |  |  | 113 | 100.0 % |
| 3+2 | 7 | 30 |  | 37 | 81.1 % |
| not_applicable |  |  | 1000 | 1000 | 100.0 % |

Confusion `is_not_available` (rows = gold, columns = predicted)

| gold \ pred | false | true | total | recall |
|---|---|---|---|---|
| false | 1075 |  | 1075 | 100.0 % |
| true | 75 |  | 75 | 0.0 % |

Calibration, v2 merged (all questions; ECE 0.004):

| bin | count | mean predicted | observed accuracy |
|---|---|---|---|
| [0.0, 0.1) | 0 | - | - |
| [0.1, 0.2) | 0 | - | - |
| [0.2, 0.3) | 0 | - | - |
| [0.3, 0.4) | 0 | - | - |
| [0.4, 0.5) | 1 | 0.475 | 0.000 |
| [0.5, 0.6) | 8 | 0.563 | 0.500 |
| [0.6, 0.7) | 10 | 0.654 | 0.500 |
| [0.7, 0.8) | 22 | 0.754 | 0.727 |
| [0.8, 0.9) | 45 | 0.861 | 0.867 |
| [0.9, 1.0] | 22914 | 1.000 | 0.996 |


## 5. The reviewer's 74 requests

`python decision/eval_ood.py --decider decider_unsloth:decide --model decision/models/qwen35-0.8b-d01-v2` (merged; run folder
[`../../ood/runs/2026-10-10-qwen35-0.8b-d01-v2/`](../../ood/runs/2026-10-10-qwen35-0.8b-d01-v2/report.md)) and `--model .../adapters` (folder
[`../../ood/runs/2026-10-10-qwen35-0.8b-d01-v2-adapters/`](../../ood/runs/2026-10-10-qwen35-0.8b-d01-v2-adapters/report.md)). The v1 columns are the v1 model rerun on the 74 rows as they were
at commit 6a51a65 (old question set; the merged column reproduces Step 6: 90.3 %, 4 / 74), the 27B column is the Bonsai baseline of the README (also on the old rows, one call per row), rules and
constant are computed on the current 74 rows.

| question | v1 merged | v1 adapters | v2 merged | v2 adapters | 27B (one call per row) | best constant | reviewer's rules |
|---|---|---|---|---|---|---|---|
| analysis | 37.8 % | 39.2 % | 82.4 % | 74.3 % | 68.9 % | 60.8 % | 77.0 % |
| route | 82.4 % | 79.7 % | 90.5 % | 81.1 % | 94.6 % | 54.1 % | 87.8 % |
| auc_method | 21.6 % | 23.0 % | 54.1 % | 67.6 % | 18.9 % | 77.0 % | 74.3 % |
| dose_has_unit | 98.6 % | 98.6 % | 97.3 % | 97.3 % | 97.3 % | 93.2 % | 100.0 % |
| is_not_available | 85.1 % | 85.1 % | 85.1 % | 85.1 % | 85.1 % | 85.1 % | 91.9 % |
| compare_pair | 100.0 % | 100.0 % | 97.3 % | 97.3 % | 95.9 % | 94.6 % | 97.3 % |
| `asked_<parameter>` (14 pooled) | 98.6 % | 98.4 % | 98.2 % | 98.2 % | 98.2 % | 90.4 % | 90.4 % |
| macro-average of the seven | 74.9 % | 74.9 % | 86.4 % | 85.8 % | 79.9 % | 79.3 % | 88.4 % |
| **all 20, per decision** | 90.3 % | 90.1 % | 94.1 % | 93.9 % | 91.8 % | 86.6 % | 89.7 % |
| **all 20 right on a row** | 4 / 74 | 6 / 74 | 20 / 74 | 22 / 74 | 7 / 74 | 0 / 74 | 0 / 74 |

Reading the table: the only column above the others on `analysis` is v2 merged (82.4 %); v2 is above the best constant on `analysis`, `route` and the macro-average, and **below it on `auc_method`**
(54.1 % merged, 67.6 % adapters against 77.0 %) and **equal to it on `is_not_available`** (0 of 11 true cases found by either form, highest P(true) 0.013). `route`: the 27B is still better (94.6 %). The
reviewer's rules stay ahead on the macro-average (88.4 % against 86.4 % / 85.8 %) and on `auc_method`. On first requests (62): `analysis` 49 / 62 merged, 43 / 62 adapters (v1: 16 / 62);
gold `nca` (45 requests) answered `nca` 38 times by the merged file, 31 by the adapters (v1: 0); the 12 follow-ups are 12 / 12 on `analysis`, `route`, `is_not_available`, 3 / 12 on `auc_method`.
Wrong decisions: 88 (merged) and 91 (adapters), of which **71 and 77 are at confidence 0.90 or more** (v1: 135 of 143).

### Per tag, v2 merged

### Accuracy per tag (which kinds of hard requests break)

| tag | rows | decisions correct | accuracy | rows all right |
|---|---|---|---|---|
| bioequivalence | 1 | 17/20 | 85.0 % | 0.0 % |
| by-id | 2 | 35/40 | 87.5 % | 0.0 % |
| c0 | 1 | 19/20 | 95.0 % | 0.0 % |
| dose-unit-g | 1 | 18/20 | 90.0 % | 0.0 % |
| dose-unit-mcg | 1 | 18/20 | 90.0 % | 0.0 % |
| dose-without-unit | 1 | 18/20 | 90.0 % | 0.0 % |
| duration-unit-mismatch | 2 | 38/40 | 95.0 % | 0.0 % |
| duration-word | 1 | 19/20 | 95.0 % | 0.0 % |
| english-term | 1 | 19/20 | 95.0 % | 0.0 % |
| follow-up | 4 | 76/80 | 95.0 % | 0.0 % |
| iv-explicit | 1 | 18/20 | 90.0 % | 0.0 % |
| multi-subject | 1 | 19/20 | 95.0 % | 0.0 % |
| multiple-dose | 1 | 16/20 | 80.0 % | 0.0 % |
| no-dose | 1 | 18/20 | 90.0 % | 0.0 % |
| no-parameter | 1 | 18/20 | 90.0 % | 0.0 % |
| non-auc-parameter | 1 | 19/20 | 95.0 % | 0.0 % |
| out-of-scope | 4 | 67/80 | 83.8 % | 0.0 % |
| parameter-not-for-route | 5 | 90/100 | 90.0 % | 0.0 % |
| parameter-not-in-schema | 2 | 34/40 | 85.0 % | 0.0 % |
| plain | 2 | 38/40 | 95.0 % | 0.0 % |
| population | 1 | 17/20 | 85.0 % | 0.0 % |
| recall | 1 | 19/20 | 95.0 % | 0.0 % |
| route-missing | 1 | 18/20 | 90.0 % | 0.0 % |
| simulate | 1 | 19/20 | 95.0 % | 0.0 % |
| steady-state | 1 | 16/20 | 80.0 % | 0.0 % |
| terminology-mismatch | 2 | 36/40 | 90.0 % | 0.0 % |
| tlag | 1 | 18/20 | 90.0 % | 0.0 % |
| unicode | 1 | 19/20 | 95.0 % | 0.0 % |
| unit-variety | 1 | 19/20 | 95.0 % | 0.0 % |
| unrecognized-unit | 1 | 18/20 | 90.0 % | 0.0 % |
| urine | 1 | 17/20 | 85.0 % | 0.0 % |
| compare | 8 | 148/160 | 92.5 % | 12.5 % |
| invented | 16 | 296/320 | 92.5 % | 12.5 % |
| abbreviation | 17 | 320/340 | 94.1 % | 17.6 % |
| unit-in-text | 5 | 95/100 | 95.0 % | 20.0 % |
| rerun | 4 | 76/80 | 95.0 % | 25.0 % |
| dose-unit-micro | 9 | 171/180 | 95.0 % | 33.3 % |
| latin-route | 3 | 58/60 | 96.7 % | 33.3 % |
| route-stated | 8 | 153/160 | 95.6 % | 37.5 % |
| route-implied | 5 | 95/100 | 95.0 % | 40.0 % |
| infusion | 7 | 135/140 | 96.4 % | 42.9 % |
| language-mix | 2 | 39/40 | 97.5 % | 50.0 % |
| method-explicit | 2 | 39/40 | 97.5 % | 50.0 % |
| typo | 2 | 39/40 | 97.5 % | 50.0 % |
| colloquial | 6 | 117/120 | 97.5 % | 66.7 % |
| blq | 4 | 79/80 | 98.8 % | 75.0 % |
| fit | 4 | 79/80 | 98.8 % | 75.0 % |
| dose-unit-mg | 1 | 20/20 | 100.0 % | 100.0 % |
| no-prior-analysis | 1 | 20/20 | 100.0 % | 100.0 % |
| oral | 1 | 20/20 | 100.0 % | 100.0 % |
| two-compartments | 2 | 40/40 | 100.0 % | 100.0 % |
| two-requests-in-one-sentence | 2 | 40/40 | 100.0 % | 100.0 % |
| unit-conversion-in-text | 1 | 20/20 | 100.0 % | 100.0 % |

Tags that broke (share of fully correct rows below the overall share): abbreviation, bioequivalence, by-id, c0, compare, dose-unit-g, dose-unit-mcg, dose-without-unit, duration-unit-mismatch, duration-word, english-term, follow-up, invented, iv-explicit, multi-subject, multiple-dose, no-dose, no-parameter, non-auc-parameter, out-of-scope, parameter-not-for-route, parameter-not-in-schema, plain, population, recall, rerun, route-missing, simulate, steady-state, terminology-mismatch, tlag, unicode, unit-in-text, unit-variety, unrecognized-unit, urine.

### Every wrong decision, v2 merged

### Wrong decisions (88)

| row | question | gold | predicted | confidence | request |
|---|---|---|---|---|---|
| ood-002 | auc_method | linear | not_applicable | 1.00 | et la t1/2 stp ? |
| ood-003 | auc_method | linear | not_applicable | 1.00 | AUC0-t et AUC0-inf svp |
| ood-004 | auc_method | linear | not_applicable | 1.00 | bolus IV de 200 mg ; quel est le Vd ? |
| ood-005 | analysis | nca | not_supported | 0.63 | bolus de 200 mg : Cl/F ? |
| ood-005 | auc_method | linear | not_applicable | 1.00 | bolus de 200 mg : Cl/F ? |
| ood-007 | route | iv_bolus | unknown | 0.52 | fit un modèle mono-compartiment sur ces données (bolus de 300 mg) |
| ood-009 | auc_method | linear | not_applicable | 1.00 | Et la MRT ? |
| ood-010 | asked_auclast | false | true | 1.00 | Perfusion de 500 µg pendant 1,5 h, Cmax et AUC0-inf. |
| ood-011 | analysis | nca | none_needed | 0.56 | Perfusion de 500 µg pendant 90 minutes : que vaut l'AUC(0-t) ? |
| ood-012 | asked_aucinf | false | true | 0.93 | J'ai avalé 800 µg, les temps sont en minutes ; Cmax et AUC0-t. |
| ood-012 | route | oral | unknown | 1.00 | J'ai avalé 800 µg, les temps sont en minutes ; Cmax et AUC0-t. |
| ood-013 | asked_auclast | true | false | 0.99 | Compare l'AUC linéaire et la lin-up/log-down. |
| ood-014 | asked_aucpext | false | true | 1.00 | Compare les deux AUC (valeur et %). |
| ood-014 | auc_method | linear | not_applicable | 1.00 | Compare les deux AUC (valeur et %). |
| ood-015 | auc_method | lin_up_log_down | not_applicable | 1.00 | Compare l'analyse 2 à l'analyse 1. |
| ood-015 | compare_pair | 3+2 | 2+3 | 0.95 | Compare l'analyse 2 à l'analyse 1. |
| ood-016 | analysis | nca | none_needed | 1.00 | Voie orale, 300 mg : y a-t-il un Tlag ? |
| ood-016 | auc_method | linear | not_applicable | 1.00 | Voie orale, 300 mg : y a-t-il un Tlag ? |
| ood-017 | auc_method | linear | not_applicable | 1.00 | Quel est le Tlag de ce bolus de 200 mg ? |
| ood-017 | is_not_available | true | false | 1.00 | Quel est le Tlag de ce bolus de 200 mg ? |
| ood-018 | auc_method | linear | not_applicable | 1.00 | Quelle est la C0 après cette prise orale de 400 mg ? |
| ood-018 | is_not_available | true | false | 1.00 | Quelle est la C0 après cette prise orale de 400 mg ? |
| ood-019 | analysis | none_needed | not_supported | 1.00 | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-019 | is_not_available | true | false | 1.00 | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-019 | route | oral | unknown | 1.00 | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-020 | analysis | none_needed | nca | 0.59 | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. |
| ood-020 | is_not_available | true | false | 1.00 | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. |
| ood-020 | route | oral | unknown | 1.00 | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. |
| ood-021 | analysis | nca | none_needed | 0.99 | Après une prise orale, voici mes concentrations : quelle est la demi-vie ? |
| ood-021 | auc_method | linear | not_applicable | 1.00 | Après une prise orale, voici mes concentrations : quelle est la demi-vie ? |
| ood-022 | analysis | nca | none_needed | 0.66 | Prise orale de 100, voici les données. Cmax ? |
| ood-022 | auc_method | linear | not_applicable | 1.00 | Prise orale de 100, voici les données. Cmax ? |
| ood-024 | auc_method | linear | not_applicable | 0.79 | Bolus de 2000 mcg : CL et Vz. |
| ood-024 | dose_has_unit | false | true | 1.00 | Bolus de 2000 mcg : CL et Vz. |
| ood-025 | auc_method | linear | not_applicable | 1.00 | Et le pourcentage d'AUC extrapolée ? |
| ood-027 | analysis | simulate | nca | 0.66 | Simule les concentrations après une dose orale de 300 mg. |
| ood-030 | asked_aucinf | false | true | 0.93 | Refais l'analyse en lin-up/log-down et compare les deux AUC en valeur et en %. |
| ood-030 | asked_aucpext | false | true | 1.00 | Refais l'analyse en lin-up/log-down et compare les deux AUC en valeur et en %. |
| ood-034 | analysis | none_needed | nca | 0.65 | Bolus de 150 mg : quel est le Vdss ? |
| ood-034 | asked_vz | false | true | 1.00 | Bolus de 150 mg : quel est le Vdss ? |
| ood-034 | auc_method | linear | not_applicable | 0.96 | Bolus de 150 mg : quel est le Vdss ? |
| ood-034 | is_not_available | true | false | 1.00 | Bolus de 150 mg : quel est le Vdss ? |
| ood-035 | auc_method | linear | not_applicable | 0.98 | Bolus de 150 mg : le R² ajusté et le nombre de points de la régression terminale. |
| ood-038 | auc_method | linear | not_applicable | 1.00 | Quel est le Tlag de cette perfusion de 150 mg ? |
| ood-038 | is_not_available | true | false | 1.00 | Quel est le Tlag de cette perfusion de 150 mg ? |
| ood-039 | asked_auclast | false | true | 1.00 | Dose IV de 1000 µg : AUC(0-inf) et pourcentage extrapolé. |
| ood-039 | route | iv_bolus | iv_infusion | 1.00 | Dose IV de 1000 µg : AUC(0-inf) et pourcentage extrapolé. |
| ood-040 | auc_method | linear | not_applicable | 1.00 | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? |
| ood-040 | route | oral | unknown | 1.00 | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? |
| ood-041 | auc_method | linear | not_applicable | 0.71 | Bolus de 200 mg à t=0, temps en minutes : Cmax et Tmax. |
| ood-043 | auc_method | linear | not_applicable | 0.79 | Perfusion IV de 150 mg sur 2 h, CL et Vz svp. |
| ood-046 | analysis | nca | none_needed | 1.00 | Bolus de 150 mg : le Cl/F et le Vz/F ? |
| ood-046 | auc_method | linear | not_applicable | 0.70 | Bolus de 150 mg : le Cl/F et le Vz/F ? |
| ood-047 | auc_method | linear | not_applicable | 1.00 | Voie orale, 100 mg : λz et t½. |
| ood-048 | auc_method | linear | not_applicable | 1.00 | Voie orale, 300 mg : quelle est la constante d'absorption ka ? |
| ood-048 | is_not_available | true | false | 1.00 | Voie orale, 300 mg : quelle est la constante d'absorption ka ? |
| ood-049 | auc_method | linear | not_applicable | 0.88 | Cmax et nombre de points de la régression terminale, dose orale de 100 mg. |
| ood-052 | asked_aucinf | false | true | 0.96 | Dose orale de 500 mg, méthode des trapèzes linéaires : AUC0-t. |
| ood-053 | analysis | nca | none_needed | 1.00 | Voici mes concentrations après 400 mg ; quel est le Cmax ? |
| ood-053 | auc_method | linear | not_applicable | 1.00 | Voici mes concentrations après 400 mg ; quel est le Cmax ? |
| ood-054 | auc_method | linear | not_applicable | 0.66 | Après une injection intraveineuse directe de 200 mg : C0 et Vz. |
| ood-055 | auc_method | linear | not_applicable | 0.99 | Perfusion de 500 µg sur 90 min : Cmax. |
| ood-056 | auc_method | linear | not_applicable | 1.00 | Rappelle-moi la dose et la méthode d'AUC utilisées. |
| ood-057 | auc_method | linear | not_applicable | 1.00 | Compare le Cmax entre les deux méthodes. |
| ood-059 | asked_auclast | false | true | 1.00 | 250 mg per os, voici les concentrations en µg/mL : Cmax, Tmax et AUC0-inf. |
| ood-060 | auc_method | linear | not_applicable | 1.00 | Bolus IV de 120 mg : quel est le Tlag ? |
| ood-060 | is_not_available | true | false | 1.00 | Bolus IV de 120 mg : quel est le Tlag ? |
| ood-061 | auc_method | linear | not_applicable | 1.00 | Quelle est la C0 après cette prise orale de 200 mg ? |
| ood-061 | is_not_available | true | false | 1.00 | Quelle est la C0 après cette prise orale de 200 mg ? |
| ood-062 | auc_method | linear | not_applicable | 1.00 | Perfusion de 75 mg sur 1,5 h, les temps sont en minutes : Cmax. |
| ood-063 | asked_aucinf | false | true | 1.00 | Étude à deux sujets, 300 mg par voie orale : Cmax et AUC0-t par sujet. |
| ood-064 | analysis | none_needed | nca | 0.63 | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-064 | asked_cmax | false | true | 1.00 | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-064 | is_not_available | true | false | 1.00 | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-064 | route | oral | unknown | 1.00 | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-065 | analysis | none_needed | not_supported | 0.99 | Recueil urinaire : quantité excrétée et clairance rénale. |
| ood-065 | asked_cl | false | true | 1.00 | Recueil urinaire : quantité excrétée et clairance rénale. |
| ood-065 | is_not_available | true | false | 1.00 | Recueil urinaire : quantité excrétée et clairance rénale. |
| ood-067 | auc_method | linear | not_applicable | 0.98 | Voie orale 1200 mg, temps en minutes : t1/2 et MRT. |
| ood-068 | asked_aucinf | false | true | 0.72 | 80 mg per os, il y a des zéros sous la LLOQ : AUC(0-t) et Cmax. |
| ood-069 | asked_aucinf | false | true | 1.00 | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. |
| ood-069 | dose_has_unit | false | true | 1.00 | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. |
| ood-071 | asked_auclast | true | false | 0.85 | Compare l'AUC linéaire et la lin-up/log-down. |
| ood-072 | asked_auclast | true | false | 1.00 | Compare l'analyse 2 et l'analyse 1 pour l'AUC. |
| ood-072 | auc_method | lin_up_log_down | not_applicable | 1.00 | Compare l'analyse 2 et l'analyse 1 pour l'AUC. |
| ood-072 | compare_pair | 3+2 | 2+3 | 0.65 | Compare l'analyse 2 et l'analyse 1 pour l'AUC. |
| ood-073 | asked_aucinf | false | true | 1.00 | Prise orale de 200 mg : Cmax, Tmax et AUC0-t. |
| ood-074 | asked_auclast | false | true | 1.00 | Bolus de 120 mg : Cmax et AUC0-inf. |

### Per tag, v2 adapters

### Accuracy per tag (which kinds of hard requests break)

| tag | rows | decisions correct | accuracy | rows all right |
|---|---|---|---|---|
| bioequivalence | 1 | 17/20 | 85.0 % | 0.0 % |
| by-id | 2 | 35/40 | 87.5 % | 0.0 % |
| compare | 8 | 147/160 | 91.9 % | 0.0 % |
| dose-unit-g | 1 | 18/20 | 90.0 % | 0.0 % |
| dose-unit-mcg | 1 | 18/20 | 90.0 % | 0.0 % |
| dose-unit-micro | 9 | 163/180 | 90.6 % | 0.0 % |
| dose-without-unit | 1 | 18/20 | 90.0 % | 0.0 % |
| duration-unit-mismatch | 2 | 36/40 | 90.0 % | 0.0 % |
| duration-word | 1 | 18/20 | 90.0 % | 0.0 % |
| english-term | 1 | 19/20 | 95.0 % | 0.0 % |
| follow-up | 4 | 76/80 | 95.0 % | 0.0 % |
| iv-explicit | 1 | 18/20 | 90.0 % | 0.0 % |
| multi-subject | 1 | 19/20 | 95.0 % | 0.0 % |
| multiple-dose | 1 | 15/20 | 75.0 % | 0.0 % |
| no-dose | 1 | 18/20 | 90.0 % | 0.0 % |
| no-parameter | 1 | 18/20 | 90.0 % | 0.0 % |
| no-prior-analysis | 1 | 19/20 | 95.0 % | 0.0 % |
| non-auc-parameter | 1 | 19/20 | 95.0 % | 0.0 % |
| out-of-scope | 4 | 66/80 | 82.5 % | 0.0 % |
| parameter-not-for-route | 5 | 89/100 | 89.0 % | 0.0 % |
| parameter-not-in-schema | 2 | 36/40 | 90.0 % | 0.0 % |
| plain | 2 | 38/40 | 95.0 % | 0.0 % |
| population | 1 | 17/20 | 85.0 % | 0.0 % |
| recall | 1 | 19/20 | 95.0 % | 0.0 % |
| rerun | 4 | 75/80 | 93.8 % | 0.0 % |
| route-missing | 1 | 18/20 | 90.0 % | 0.0 % |
| steady-state | 1 | 15/20 | 75.0 % | 0.0 % |
| terminology-mismatch | 2 | 37/40 | 92.5 % | 0.0 % |
| tlag | 1 | 18/20 | 90.0 % | 0.0 % |
| unicode | 1 | 19/20 | 95.0 % | 0.0 % |
| unit-variety | 1 | 19/20 | 95.0 % | 0.0 % |
| unrecognized-unit | 1 | 18/20 | 90.0 % | 0.0 % |
| urine | 1 | 17/20 | 85.0 % | 0.0 % |
| invented | 16 | 292/320 | 91.2 % | 12.5 % |
| infusion | 7 | 131/140 | 93.6 % | 28.6 % |
| latin-route | 3 | 58/60 | 96.7 % | 33.3 % |
| route-implied | 5 | 95/100 | 95.0 % | 40.0 % |
| abbreviation | 17 | 327/340 | 96.2 % | 41.2 % |
| blq | 4 | 78/80 | 97.5 % | 50.0 % |
| colloquial | 6 | 114/120 | 95.0 % | 50.0 % |
| language-mix | 2 | 39/40 | 97.5 % | 50.0 % |
| method-explicit | 2 | 39/40 | 97.5 % | 50.0 % |
| two-requests-in-one-sentence | 2 | 39/40 | 97.5 % | 50.0 % |
| typo | 2 | 39/40 | 97.5 % | 50.0 % |
| unit-in-text | 5 | 96/100 | 96.0 % | 60.0 % |
| route-stated | 8 | 155/160 | 96.9 % | 62.5 % |
| fit | 4 | 79/80 | 98.8 % | 75.0 % |
| c0 | 1 | 20/20 | 100.0 % | 100.0 % |
| dose-unit-mg | 1 | 20/20 | 100.0 % | 100.0 % |
| oral | 1 | 20/20 | 100.0 % | 100.0 % |
| simulate | 1 | 20/20 | 100.0 % | 100.0 % |
| two-compartments | 2 | 40/40 | 100.0 % | 100.0 % |
| unit-conversion-in-text | 1 | 20/20 | 100.0 % | 100.0 % |

Tags that broke (share of fully correct rows below the overall share): bioequivalence, by-id, compare, dose-unit-g, dose-unit-mcg, dose-unit-micro, dose-without-unit, duration-unit-mismatch, duration-word, english-term, follow-up, infusion, invented, iv-explicit, multi-subject, multiple-dose, no-dose, no-parameter, no-prior-analysis, non-auc-parameter, out-of-scope, parameter-not-for-route, parameter-not-in-schema, plain, population, recall, rerun, route-missing, steady-state, terminology-mismatch, tlag, unicode, unit-variety, unrecognized-unit, urine.

### Every wrong decision, v2 adapters

### Wrong decisions (91)

| row | question | gold | predicted | confidence | request |
|---|---|---|---|---|---|
| ood-002 | auc_method | linear | not_applicable | 1.00 | et la t1/2 stp ? |
| ood-003 | auc_method | linear | not_applicable | 1.00 | AUC0-t et AUC0-inf svp |
| ood-005 | analysis | nca | none_needed | 0.94 | bolus de 200 mg : Cl/F ? |
| ood-005 | auc_method | linear | not_applicable | 1.00 | bolus de 200 mg : Cl/F ? |
| ood-007 | route | iv_bolus | unknown | 0.52 | fit un modèle mono-compartiment sur ces données (bolus de 300 mg) |
| ood-009 | auc_method | linear | not_applicable | 1.00 | Et la MRT ? |
| ood-010 | asked_auclast | false | true | 1.00 | Perfusion de 500 µg pendant 1,5 h, Cmax et AUC0-inf. |
| ood-010 | route | iv_infusion | unknown | 1.00 | Perfusion de 500 µg pendant 1,5 h, Cmax et AUC0-inf. |
| ood-011 | analysis | nca | none_needed | 0.96 | Perfusion de 500 µg pendant 90 minutes : que vaut l'AUC(0-t) ? |
| ood-011 | route | iv_infusion | unknown | 1.00 | Perfusion de 500 µg pendant 90 minutes : que vaut l'AUC(0-t) ? |
| ood-012 | asked_aucinf | false | true | 1.00 | J'ai avalé 800 µg, les temps sont en minutes ; Cmax et AUC0-t. |
| ood-012 | route | oral | unknown | 1.00 | J'ai avalé 800 µg, les temps sont en minutes ; Cmax et AUC0-t. |
| ood-013 | asked_auclast | true | false | 1.00 | Compare l'AUC linéaire et la lin-up/log-down. |
| ood-014 | asked_aucpext | false | true | 1.00 | Compare les deux AUC (valeur et %). |
| ood-014 | auc_method | linear | not_applicable | 1.00 | Compare les deux AUC (valeur et %). |
| ood-015 | auc_method | lin_up_log_down | not_applicable | 1.00 | Compare l'analyse 2 à l'analyse 1. |
| ood-015 | compare_pair | 3+2 | 2+3 | 1.00 | Compare l'analyse 2 à l'analyse 1. |
| ood-016 | analysis | nca | none_needed | 0.98 | Voie orale, 300 mg : y a-t-il un Tlag ? |
| ood-016 | auc_method | linear | not_applicable | 1.00 | Voie orale, 300 mg : y a-t-il un Tlag ? |
| ood-017 | auc_method | linear | not_applicable | 1.00 | Quel est le Tlag de ce bolus de 200 mg ? |
| ood-017 | is_not_available | true | false | 0.99 | Quel est le Tlag de ce bolus de 200 mg ? |
| ood-018 | auc_method | linear | not_applicable | 1.00 | Quelle est la C0 après cette prise orale de 400 mg ? |
| ood-018 | is_not_available | true | false | 0.99 | Quelle est la C0 après cette prise orale de 400 mg ? |
| ood-019 | analysis | none_needed | not_supported | 1.00 | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-019 | is_not_available | true | false | 1.00 | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-019 | route | oral | unknown | 1.00 | Ce produit de 400 mg est-il bioéquivalent au princeps ? |
| ood-020 | analysis | none_needed | not_supported | 1.00 | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. |
| ood-020 | is_not_available | true | false | 1.00 | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. |
| ood-020 | route | oral | unknown | 1.00 | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. |
| ood-021 | analysis | nca | none_needed | 0.87 | Après une prise orale, voici mes concentrations : quelle est la demi-vie ? |
| ood-021 | auc_method | linear | not_applicable | 1.00 | Après une prise orale, voici mes concentrations : quelle est la demi-vie ? |
| ood-022 | analysis | nca | none_needed | 0.98 | Prise orale de 100, voici les données. Cmax ? |
| ood-022 | auc_method | linear | not_applicable | 0.91 | Prise orale de 100, voici les données. Cmax ? |
| ood-024 | analysis | nca | none_needed | 0.73 | Bolus de 2000 mcg : CL et Vz. |
| ood-024 | dose_has_unit | false | true | 1.00 | Bolus de 2000 mcg : CL et Vz. |
| ood-025 | auc_method | linear | not_applicable | 1.00 | Et le pourcentage d'AUC extrapolée ? |
| ood-029 | route | iv_bolus | unknown | 0.91 | Donne-moi le Cmax puis refais l'analyse en lin-up/log-down, bolus de 300 mg. |
| ood-030 | asked_aucinf | false | true | 0.98 | Refais l'analyse en lin-up/log-down et compare les deux AUC en valeur et en %. |
| ood-030 | asked_aucpext | false | true | 1.00 | Refais l'analyse en lin-up/log-down et compare les deux AUC en valeur et en %. |
| ood-034 | asked_vz | false | true | 1.00 | Bolus de 150 mg : quel est le Vdss ? |
| ood-034 | is_not_available | true | false | 1.00 | Bolus de 150 mg : quel est le Vdss ? |
| ood-037 | route | iv_infusion | unknown | 1.00 | Perfusion de 150 mg sur 2 h : clairance et volume de distribution. |
| ood-038 | auc_method | linear | not_applicable | 1.00 | Quel est le Tlag de cette perfusion de 150 mg ? |
| ood-038 | is_not_available | true | false | 0.99 | Quel est le Tlag de cette perfusion de 150 mg ? |
| ood-039 | asked_auclast | false | true | 1.00 | Dose IV de 1000 µg : AUC(0-inf) et pourcentage extrapolé. |
| ood-039 | route | iv_bolus | iv_infusion | 1.00 | Dose IV de 1000 µg : AUC(0-inf) et pourcentage extrapolé. |
| ood-040 | analysis | nca | none_needed | 0.60 | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? |
| ood-040 | auc_method | linear | not_applicable | 1.00 | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? |
| ood-040 | route | oral | unknown | 1.00 | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? |
| ood-044 | route | oral | unknown | 1.00 | Comprimé à libération prolongée de 5000 µg : Cmax, Tmax et demi-vie. |
| ood-046 | analysis | nca | none_needed | 1.00 | Bolus de 150 mg : le Cl/F et le Vz/F ? |
| ood-047 | auc_method | linear | not_applicable | 0.96 | Voie orale, 100 mg : λz et t½. |
| ood-048 | auc_method | linear | not_applicable | 1.00 | Voie orale, 300 mg : quelle est la constante d'absorption ka ? |
| ood-048 | is_not_available | true | false | 0.99 | Voie orale, 300 mg : quelle est la constante d'absorption ka ? |
| ood-051 | analysis | nca | none_needed | 0.71 | Bolus de 2000 µg : l'AUC(0-t) tient-elle compte du point sous la LLOQ ? et le % extrapolé ? |
| ood-052 | asked_aucinf | false | true | 1.00 | Dose orale de 500 mg, méthode des trapèzes linéaires : AUC0-t. |
| ood-053 | analysis | nca | none_needed | 1.00 | Voici mes concentrations après 400 mg ; quel est le Cmax ? |
| ood-053 | auc_method | linear | not_applicable | 0.70 | Voici mes concentrations après 400 mg ; quel est le Cmax ? |
| ood-055 | analysis | nca | none_needed | 0.98 | Perfusion de 500 µg sur 90 min : Cmax. |
| ood-055 | route | iv_infusion | unknown | 1.00 | Perfusion de 500 µg sur 90 min : Cmax. |
| ood-056 | auc_method | linear | not_applicable | 1.00 | Rappelle-moi la dose et la méthode d'AUC utilisées. |
| ood-057 | auc_method | linear | not_applicable | 1.00 | Compare le Cmax entre les deux méthodes. |
| ood-058 | asked_aucinf | false | true | 0.52 | Compare les AUC linéaire et lin-up/log-down, dose orale de 400 mg. |
| ood-059 | asked_auclast | false | true | 1.00 | 250 mg per os, voici les concentrations en µg/mL : Cmax, Tmax et AUC0-inf. |
| ood-060 | auc_method | linear | not_applicable | 0.75 | Bolus IV de 120 mg : quel est le Tlag ? |
| ood-060 | is_not_available | true | false | 0.99 | Bolus IV de 120 mg : quel est le Tlag ? |
| ood-061 | analysis | none_needed | nca | 0.98 | Quelle est la C0 après cette prise orale de 200 mg ? |
| ood-061 | auc_method | linear | not_applicable | 1.00 | Quelle est la C0 après cette prise orale de 200 mg ? |
| ood-061 | is_not_available | true | false | 0.99 | Quelle est la C0 après cette prise orale de 200 mg ? |
| ood-062 | analysis | nca | none_needed | 0.66 | Perfusion de 75 mg sur 1,5 h, les temps sont en minutes : Cmax. |
| ood-062 | auc_method | linear | not_applicable | 0.76 | Perfusion de 75 mg sur 1,5 h, les temps sont en minutes : Cmax. |
| ood-063 | asked_aucinf | false | true | 1.00 | Étude à deux sujets, 300 mg par voie orale : Cmax et AUC0-t par sujet. |
| ood-064 | analysis | none_needed | not_supported | 1.00 | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-064 | asked_cmax | false | true | 1.00 | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-064 | auc_method | not_applicable | linear | 0.59 | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-064 | is_not_available | true | false | 1.00 | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-064 | route | oral | unknown | 1.00 | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. |
| ood-065 | analysis | none_needed | not_supported | 1.00 | Recueil urinaire : quantité excrétée et clairance rénale. |
| ood-065 | asked_cl | false | true | 1.00 | Recueil urinaire : quantité excrétée et clairance rénale. |
| ood-065 | is_not_available | true | false | 1.00 | Recueil urinaire : quantité excrétée et clairance rénale. |
| ood-068 | analysis | nca | none_needed | 0.69 | 80 mg per os, il y a des zéros sous la LLOQ : AUC(0-t) et Cmax. |
| ood-069 | asked_aucinf | false | true | 1.00 | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. |
| ood-069 | dose_has_unit | false | true | 1.00 | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. |
| ood-070 | analysis | nca | none_needed | 0.91 | Perfusion de 750 µg sur 1 h : Vz et CL. |
| ood-070 | route | iv_infusion | unknown | 1.00 | Perfusion de 750 µg sur 1 h : Vz et CL. |
| ood-071 | asked_auclast | true | false | 0.83 | Compare l'AUC linéaire et la lin-up/log-down. |
| ood-072 | asked_auclast | true | false | 1.00 | Compare l'analyse 2 et l'analyse 1 pour l'AUC. |
| ood-072 | auc_method | lin_up_log_down | not_applicable | 1.00 | Compare l'analyse 2 et l'analyse 1 pour l'AUC. |
| ood-072 | compare_pair | 3+2 | 2+3 | 0.86 | Compare l'analyse 2 et l'analyse 1 pour l'AUC. |
| ood-073 | asked_aucinf | false | true | 1.00 | Prise orale de 200 mg : Cmax, Tmax et AUC0-t. |
| ood-074 | asked_auclast | false | true | 1.00 | Bolus de 120 mg : Cmax et AUC0-inf. |


## 6. The harness

### 6.1 The 25 benchmark exercises (`python decision/run_harness.py --decider decider_unsloth:decide --model ...`)

| pipeline | oracle-correct turns | oracle-correct numbers | invalid or failed tool calls | gate: unverified numbers | scorer turns | s per turn | model s per call | GPU torch peak |
|---|---|---|---|---|---|---|---|---|
| decision harness, v1 merged (Step 5) | 175 / 175 | 558 / 558 | 0 / 250 | 0 / 709 | 200 / 200 | 0.34 | 0.197 | 1.9 GB |
| v2 merged ([`../2026-10-10-harness-qwen35-0.8b-d01-v2/`](../2026-10-10-harness-qwen35-0.8b-d01-v2/report.md)) | **175 / 175** | **558 / 558** | 0 / 250 | 0 / 807 | 200 / 200 | 0.336 | 0.200 | 1941 MiB |
| v2 adapters ([`../2026-10-10-harness-qwen35-0.8b-d01-v2-adapters/`](../2026-10-10-harness-qwen35-0.8b-d01-v2-adapters/report.md)) | **175 / 175** | **558 / 558** | 0 / 250 | 0 / 778 | 200 / 200 | 0.375 | 0.225 | 1440 MiB (2325 MiB `nvidia-smi`) |

Oracle and scorer agree on every turn in both runs. Decisions that differ from the gold ones (4500 asked): v2 merged **50** (25 `compare_pair` on the first compare ask, which the harness does not use, and **25 of 25
`is_not_available` on the not-available turns**, answered `false` at confidence 1.0); v2 adapters **25** (the 25 `compare_pair` asks only). With the merged file the not-available turns take the reading path
and answer with the engine's own sentence ("C0 ... n'est pas calculé par Caladrius (« not defined for this route of administration »)" preceded by the header line) instead of the refusal template; the
oracle does not cover that kind and the scorer expects no number, so both score it correct and cannot tell the two answers apart. The 175 / 175 therefore does not discriminate between the two forms.

### 6.2 The 74 requests through the harness (one fresh Caladrius session per request, prior analyses replayed first)

| | v1 merged (Step 6) | v2 merged | v2 adapters | gold decisions (`2026-10-10-ood-gold`) |
|---|---|---|---|---|
| answers with values | 12 | 44 | 38 | 47 |
| "Aucune analyse n'est encore faite" (`refusal:no-analysis`) | 58 | 13 | 20 | 1 |
| asked back (dose unit, route, duration: `refusal:ask`) | 0 | 9 | 6 | 7 |
| parameter not available (`refusal:not-available`) | 0 | 0 | 1 | 5 |
| not supported (`refusal:not-supported`) / no parameter | 0 | 3 / 1 | 4 / 0 | see next row |
| not wired (fit, simulate; for the gold column also the not-supported ones, which that run filed here) | 4 | 4 | 5 | 11 |
| which pair | 0 | 0 | 0 | 3 |
| errors | 0 | 0 | 0 | 0 |
| answered where the gold decisions expect a refusal or a question ("dangerous direction") | 0 | **3** (ood-024, 034, 069) | **2** (ood-061, 069) | 0 |
| refused or asked where the gold decisions expect an answer | | 12 | 17 | 12 (harness limits, see Harness fixes) |
| decisions outside the options / state differs from the scored row | 0 / 0 | 0 / 0 | 0 / 0 | |

The dangerous-direction answers, read: ood-034 ("Bolus de 150 mg : quel est le Vdss ?") gets the Vz line (labelled Vz) and no word on Vdss, a real defect (`is_not_available` missed, `asked_vz` guessed);
ood-024 ("2000 mcg") and ood-069 ("0,25 g") are answered with the dose as the user wrote it and Caladrius's conversion, which the reviewer's gold counts as "ask" (`dose_has_unit` false); ood-061 (adapters,
"C0 après cette prise orale") is answered with the engine's own "not calculated for this route" statement, content right, template different. The list of requests a human must read is 64 of 74 in both runs
(wrong decision, answer contradicting the gold decisions, or a tag that broke); the full text of every answer is in the `answers.jsonl` of each ood run folder. For v2 merged:

| request id | request | why a human reads it |
|---|---|---|
| ood-001 | J'ai pris un comprimé de 400 mg ce matin, voici mes concentrations. C'est quoi le Cmax et le Tmax ? | wrong decision: auc_method |
| ood-002 | et la t1/2 stp ? | wrong decision: auc_method; tag that broke: abbreviation; tag that broke: follow-up |
| ood-003 | AUC0-t et AUC0-inf svp | wrong decision: auc_method; tag that broke: abbreviation; tag that broke: follow-up |
| ood-004 | bolus IV de 200 mg ; quel est le Vd ? | wrong decision: auc_method; tag that broke: abbreviation |
| ood-005 | bolus de 200 mg : Cl/F ? | wrong decision: analysis, auc_method, route; refused / asked (not-supported) where the gold decisions expect an answer; tag that broke: abbreviation; tag that broke: terminology-mismatch |
| ood-009 | Et la MRT ? | wrong decision: auc_method; tag that broke: abbreviation; tag that broke: follow-up |
| ood-010 | Perfusion de 500 µg pendant 1,5 h, Cmax et AUC0-inf. | wrong decision: asked_auclast, route; refused / asked (ask) where the gold decisions expect an answer; tag that broke: duration-unit-mismatch; tag that broke: unit-in-text |
| ood-011 | Perfusion de 500 µg pendant 90 minutes : que vaut l'AUC(0-t) ? | wrong decision: analysis, auc_method, route; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: duration-word |
| ood-012 | J'ai avalé 800 µg, les temps sont en minutes ; Cmax et AUC0-t. | wrong decision: route; refused / asked (ask) where the gold decisions expect an answer; tag that broke: abbreviation |
| ood-013 | Compare l'AUC linéaire et la lin-up/log-down. | wrong decision: asked_auclast; tag that broke: compare; tag that broke: english-term; tag that broke: rerun |
| ood-014 | Compare les deux AUC (valeur et %). | wrong decision: asked_auclast, auc_method; tag that broke: compare |
| ood-015 | Compare l'analyse 2 à l'analyse 1. | wrong decision: auc_method, compare_pair; tag that broke: compare; tag that broke: by-id; tag that broke: no-parameter |
| ood-016 | Voie orale, 300 mg : y a-t-il un Tlag ? | wrong decision: analysis, asked_tmax, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: tlag |
| ood-017 | Quel est le Tlag de ce bolus de 200 mg ? | wrong decision: auc_method, is_not_available; tag that broke: parameter-not-for-route; tag that broke: iv-explicit |
| ood-018 | Quelle est la C0 après cette prise orale de 400 mg ? | wrong decision: auc_method, is_not_available; tag that broke: parameter-not-for-route |
| ood-019 | Ce produit de 400 mg est-il bioéquivalent au princeps ? | wrong decision: analysis, is_not_available, route; tag that broke: out-of-scope; tag that broke: bioequivalence |
| ood-020 | Estime un modèle de population à effets mixtes (NONMEM) sur ces données, dose 400 mg. | wrong decision: analysis, is_not_available, route; tag that broke: out-of-scope; tag that broke: population |
| ood-021 | Après une prise orale, voici mes concentrations : quelle est la demi-vie ? | wrong decision: analysis, auc_method; tag that broke: no-dose |
| ood-022 | Prise orale de 100, voici les données. Cmax ? | wrong decision: analysis, auc_method; tag that broke: dose-without-unit |
| ood-023 | Bolus IV de 2 mg : donne-moi la clairance et le Vz. | wrong decision: auc_method |
| ood-024 | Bolus de 2000 mcg : CL et Vz. | wrong decision: auc_method, dose_has_unit; answered where the gold decisions expect a refusal; tag that broke: dose-unit-mcg; tag that broke: unrecognized-unit |
| ood-025 | Et le pourcentage d'AUC extrapolée ? | wrong decision: auc_method; tag that broke: follow-up |
| ood-027 | Simule les concentrations après une dose orale de 300 mg. | wrong decision: analysis; tag that broke: simulate |
| ood-028 | Donne-moi d'abord la demi-vie, ensuite la clairance et le Vz, pour cette dose orale de 300 mg. | wrong decision: auc_method |
| ood-029 | Donne-moi le Cmax puis refais l'analyse en lin-up/log-down, bolus de 300 mg. | tag that broke: rerun |
| ood-030 | Refais l'analyse en lin-up/log-down et compare les deux AUC en valeur et en %. | wrong decision: asked_aucpext; tag that broke: compare; tag that broke: rerun |
| ood-031 | Peux-tu me donner le Cmax, le Tmax et le t1/2 after a single oral dose of 100 mg ? | wrong decision: auc_method |
| ood-032 | kel est le Cmax é le Tmax de ce tablo ? dose 400 mg per os | wrong decision: auc_method |
| ood-034 | Bolus de 150 mg : quel est le Vdss ? | wrong decision: analysis, asked_vz, auc_method, is_not_available; answered where the gold decisions expect a refusal; tag that broke: parameter-not-in-schema |
| ood-035 | Bolus de 150 mg : le R² ajusté et le nombre de points de la régression terminale. | wrong decision: auc_method |
| ood-036 | Prise unique de 100 mg par voie orale : je veux le MRT et la demi-vie. | wrong decision: auc_method |
| ood-037 | Perfusion de 150 mg sur 2 h : clairance et volume de distribution. | wrong decision: auc_method, route; refused / asked (ask) where the gold decisions expect an answer |
| ood-038 | Quel est le Tlag de cette perfusion de 150 mg ? | wrong decision: auc_method, is_not_available; tag that broke: parameter-not-for-route |
| ood-039 | Dose IV de 1000 µg : AUC(0-inf) et pourcentage extrapolé. | wrong decision: asked_auclast, asked_c0 |
| ood-040 | J'ai ingéré 2000 µg : au bout de combien de temps la concentration est-elle divisée par deux ? | wrong decision: auc_method, route; refused / asked (ask) where the gold decisions expect an answer |
| ood-041 | Bolus de 200 mg à t=0, temps en minutes : Cmax et Tmax. | wrong decision: auc_method; tag that broke: unit-in-text |
| ood-043 | Perfusion IV de 150 mg sur 2 h, CL et Vz svp. | wrong decision: auc_method |
| ood-044 | Comprimé à libération prolongée de 5000 µg : Cmax, Tmax et demi-vie. | wrong decision: auc_method |
| ood-045 | Bolus de 300 mg, temps en minutes : AUC(0-t) et clairance. | tag that broke: unit-in-text |
| ood-046 | Bolus de 150 mg : le Cl/F et le Vz/F ? | wrong decision: analysis, auc_method; refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: terminology-mismatch |
| ood-047 | Voie orale, 100 mg : λz et t½. | wrong decision: auc_method; tag that broke: unicode |
| ood-048 | Voie orale, 300 mg : quelle est la constante d'absorption ka ? | wrong decision: auc_method, is_not_available; tag that broke: parameter-not-in-schema |
| ood-049 | Cmax et nombre de points de la régression terminale, dose orale de 100 mg. | wrong decision: auc_method |
| ood-051 | Bolus de 2000 µg : l'AUC(0-t) tient-elle compte du point sous la LLOQ ? et le % extrapolé ? | wrong decision: asked_c0 |
| ood-053 | Voici mes concentrations après 400 mg ; quel est le Cmax ? | wrong decision: analysis, auc_method; tag that broke: route-missing |
| ood-054 | Après une injection intraveineuse directe de 200 mg : C0 et Vz. | wrong decision: auc_method; tag that broke: c0 |
| ood-055 | Perfusion de 500 µg sur 90 min : Cmax. | wrong decision: auc_method, route; refused / asked (ask) where the gold decisions expect an answer |
| ood-056 | Rappelle-moi la dose et la méthode d'AUC utilisées. | wrong decision: auc_method; tag that broke: recall |
| ood-057 | Compare le Cmax entre les deux méthodes. | wrong decision: auc_method; tag that broke: compare; tag that broke: non-auc-parameter |
| ood-058 | Compare les AUC linéaire et lin-up/log-down, dose orale de 400 mg. | refused / asked (no-analysis) where the gold decisions expect an answer; tag that broke: compare |
| ood-059 | 250 mg per os, voici les concentrations en µg/mL : Cmax, Tmax et AUC0-inf. | wrong decision: asked_auclast; tag that broke: invented; tag that broke: unit-variety |
| ood-060 | Bolus IV de 120 mg : quel est le Tlag ? | wrong decision: auc_method, is_not_available; tag that broke: invented; tag that broke: parameter-not-for-route |
| ood-061 | Quelle est la C0 après cette prise orale de 200 mg ? | wrong decision: auc_method, is_not_available; tag that broke: invented; tag that broke: parameter-not-for-route |
| ood-062 | Perfusion de 75 mg sur 1,5 h, les temps sont en minutes : Cmax. | wrong decision: auc_method; refused / asked (ask) where the gold decisions expect an answer; tag that broke: invented; tag that broke: duration-unit-mismatch |
| ood-063 | Étude à deux sujets, 300 mg par voie orale : Cmax et AUC0-t par sujet. | tag that broke: invented; tag that broke: multi-subject |
| ood-064 | Administration répétée de 100 mg toutes les 12 h : Cmax à l'état d'équilibre et Cmin. | wrong decision: analysis, asked_cmax, is_not_available, route; tag that broke: invented; tag that broke: out-of-scope; tag that broke: steady-state; tag that broke: multiple-dose |
| ood-065 | Recueil urinaire : quantité excrétée et clairance rénale. | wrong decision: analysis, asked_cl, dose_has_unit, is_not_available; tag that broke: out-of-scope; tag that broke: urine |
| ood-067 | Voie orale 1200 mg, temps en minutes : t1/2 et MRT. | wrong decision: auc_method; tag that broke: unit-in-text |
| ood-069 | J'ai pris 0,25 g par voie orale : Cmax et AUC0-t. | wrong decision: dose_has_unit; answered where the gold decisions expect a refusal; tag that broke: dose-unit-g; tag that broke: unit-in-text |
| ood-070 | Perfusion de 750 µg sur 1 h : Vz et CL. | wrong decision: auc_method, route; refused / asked (ask) where the gold decisions expect an answer |
| ood-071 | Compare l'AUC linéaire et la lin-up/log-down. | wrong decision: asked_auclast; tag that broke: rerun |
| ood-072 | Compare l'analyse 2 et l'analyse 1 pour l'AUC. | wrong decision: asked_auclast, auc_method, compare_pair; tag that broke: by-id |
| ood-073 | Prise orale de 200 mg : Cmax, Tmax et AUC0-t. | tag that broke: plain |
| ood-074 | Bolus de 120 mg : Cmax et AUC0-inf. | wrong decision: asked_auclast; tag that broke: plain |

(v2 adapters: 64 requests too, list in [its report](../../ood/runs/2026-10-10-qwen35-0.8b-d01-v2-adapters/report.md).)

## 7. Relevance ablation: does the model read the concentration data?

`python decision/ablation.py --model <folder> --split heldout_both` ([`ablation.py`](../../ablation.py), tests in `tests/test_ablation.py`): the 593 rows of `heldout_both`, scored three times with the same model:
the rows as they are; the concentration column of the digest (`state.data.first_rows`, five "time,conc" lines) replaced by random values uniform between 0 and the largest value of the digest (seed 7,
the time column, header, row count, dose sentence and request untouched); the `data` key removed from the state (request, dose sentence, notes and the analyses present stay). The gold is not changed: **no
gold label of the 20 questions is computed from a concentration value** (wording, dose sentence, turn kind, analyses present), so a model that ignores the numbers is right to; the experiment asks whether the answers move.

v2 merged:


`decision/ablation.py`; none = the rows as they are, random_conc = concentrations of the digest replaced by random values of the same magnitude, no_table = the data key removed from the state. Gold unchanged (no gold label is computed from a concentration value).

| mode | decisions right | all 20 right on a row | decisions that flip against `none` |
|---|---|---|---|
| none | 11599 / 11860 = 97.80 % | 362 / 593 | - |
| random_conc | 11602 / 11860 = 97.82 % | 367 / 593 | 17 / 11860 |
| no_table | 11561 / 11860 = 97.48 % | 347 / 593 | 88 / 11860 |

Per question: accuracy without ablation, accuracy after, flips (of 593), mean absolute change of the probability of the original label.

| question | none | random_conc | flips | mean dp | no_table | flips | mean dp |
|---|---|---|---|---|---|---|---|
| analysis | 95.3 % | 95.1 % | 7 | 0.0097 | 90.1 % | 33 | 0.0567 |
| asked_adj_r2 | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_aucinf | 100.0 % | 100.0 % | 0 | 0.0003 | 100.0 % | 0 | 0.0011 |
| asked_auclast | 97.0 % | 97.0 % | 0 | 0.0000 | 98.0 % | 6 | 0.0093 |
| asked_aucpext | 99.8 % | 99.8 % | 0 | 0.0009 | 99.5 % | 2 | 0.0029 |
| asked_c0 | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_cl | 97.5 % | 97.5 % | 0 | 0.0003 | 97.5 % | 0 | 0.0008 |
| asked_cmax | 97.6 % | 97.6 % | 0 | 0.0002 | 98.8 % | 21 | 0.0338 |
| asked_half_life | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_lambda_z | 98.3 % | 98.8 % | 3 | 0.0019 | 98.8 % | 3 | 0.0033 |
| asked_lambda_z_points | 97.5 % | 97.5 % | 0 | 0.0000 | 97.5 % | 0 | 0.0000 |
| asked_mrt | 99.3 % | 99.0 % | 2 | 0.0038 | 97.0 % | 14 | 0.0207 |
| asked_tlag | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_tmax | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_vz | 96.0 % | 96.0 % | 0 | 0.0003 | 95.8 % | 1 | 0.0056 |
| auc_method | 88.0 % | 88.0 % | 0 | 0.0015 | 88.0 % | 0 | 0.0060 |
| compare_pair | 97.0 % | 97.1 % | 3 | 0.0009 | 96.6 % | 4 | 0.0029 |
| dose_has_unit | 100.0 % | 100.0 % | 0 | 0.0000 | 99.7 % | 2 | 0.0034 |
| is_not_available | 94.4 % | 94.4 % | 0 | 0.0000 | 94.4 % | 0 | 0.0000 |
| route | 98.3 % | 98.7 % | 2 | 0.0008 | 98.0 % | 2 | 0.0080 |


v2 adapters:


`decision/ablation.py`; none = the rows as they are, random_conc = concentrations of the digest replaced by random values of the same magnitude, no_table = the data key removed from the state. Gold unchanged (no gold label is computed from a concentration value).

| mode | decisions right | all 20 right on a row | decisions that flip against `none` |
|---|---|---|---|
| none | 11643 / 11860 = 98.17 % | 400 / 593 | - |
| random_conc | 11648 / 11860 = 98.21 % | 406 / 593 | 18 / 11860 |
| no_table | 11635 / 11860 = 98.10 % | 394 / 593 | 74 / 11860 |

Per question: accuracy without ablation, accuracy after, flips (of 593), mean absolute change of the probability of the original label.

| question | none | random_conc | flips | mean dp | no_table | flips | mean dp |
|---|---|---|---|---|---|---|---|
| analysis | 95.1 % | 94.9 % | 9 | 0.0092 | 92.9 % | 17 | 0.0329 |
| asked_adj_r2 | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_aucinf | 99.8 % | 100.0 % | 1 | 0.0010 | 100.0 % | 1 | 0.0019 |
| asked_auclast | 97.0 % | 97.3 % | 2 | 0.0026 | 97.8 % | 11 | 0.0183 |
| asked_aucpext | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_c0 | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_cl | 97.5 % | 97.5 % | 0 | 0.0003 | 97.5 % | 0 | 0.0006 |
| asked_cmax | 97.6 % | 97.6 % | 0 | 0.0000 | 100.0 % | 14 | 0.0236 |
| asked_half_life | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_lambda_z | 98.8 % | 98.8 % | 0 | 0.0001 | 96.5 % | 14 | 0.0207 |
| asked_lambda_z_points | 97.5 % | 97.5 % | 0 | 0.0000 | 97.5 % | 0 | 0.0000 |
| asked_mrt | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0002 |
| asked_tlag | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_tmax | 100.0 % | 100.0 % | 0 | 0.0000 | 100.0 % | 0 | 0.0000 |
| asked_vz | 96.0 % | 96.0 % | 0 | 0.0000 | 96.0 % | 0 | 0.0002 |
| auc_method | 90.7 % | 91.1 % | 3 | 0.0043 | 91.6 % | 9 | 0.0167 |
| compare_pair | 98.0 % | 98.0 % | 0 | 0.0007 | 98.0 % | 0 | 0.0029 |
| dose_has_unit | 100.0 % | 100.0 % | 0 | 0.0000 | 99.3 % | 4 | 0.0060 |
| is_not_available | 96.3 % | 96.5 % | 1 | 0.0013 | 96.0 % | 2 | 0.0037 |
| route | 99.2 % | 99.2 % | 2 | 0.0024 | 99.2 % | 2 | 0.0040 |


## 8. Reading

1. Holding out wordings and adding 163 of them made the model transfer, not fully: on the reviewer's requests `analysis` went from 37.8 % to 82.4 % (merged) / 74.3 % (adapters), `route` from 82.4 % to 90.5 % / 81.1 %, complete vectors from 4 / 74 to 20 / 74 and 22 / 74, and the
   harness answers 44 / 38 requests instead of 12; the number of requests told "no analysis" fell from 58 to 13 / 20. The model is now ahead of the 27B on complete vectors (7 / 74) and of the best constant on `analysis`, but 70 to 73 % of the requests still have at least one wrong decision,
   and on wordings it never saw but in known exercises 98.2 % per decision is only 568 / 825 complete vectors (adapters; 520 with the merged file), against 917 / 920 on new exercises in known wordings. The 99.9 % of v1 measured the generator's wordings; 98 % measures the same gap, smaller.
2. Where it still fails: `auc_method` (below the best constant on the 74: the convention "`linear` when the request names no method" is learned as `not_applicable` for follow-up and short requests, 21 to 32 of 57 `linear`), `is_not_available` (**never found on the
   reviewer's requests, 0 / 11**; 33 to 36 % recall on unseen wordings with the adapters, 0 % with the merged file, which also misses every case in distribution), `fit_pk2` asked in unseen wordings (recall 55 to 73 %, answered `none_needed`), infusions (`route` `unknown`),
   the reversed compare `3+2` (recall 28 to 61 % on unseen wordings) and everything the reviewer wrote that is far from the generator (duration units, steady state, urine, Vdss).
3. Confidence still does not warn: 71 of 88 (merged) and 77 of 91 (adapters) wrong decisions on the 74 requests are at 0.90 or more, 238 of 293 on `heldout_wordings` (adapters); ECE is 0.016 to 0.020 on unseen wordings, 0.054 to 0.057 on the 74 requests.
   The harness gate stays the guard (0 unverified numbers in all runs), not the probability.
4. The merged 16-bit file loses information the trained model has (`is_not_available` recall 0 % in distribution against 100 % for the adapters, 50 `is_not_available` and `compare_pair` decisions differing from the gold in the benchmark run against 25): the file that was shipped and measured in Steps 3, 5 and 6
   is not the model that was calibrated; use the adapters on the 4-bit base, or find out why the merge degrades (not done here), before quoting a figure for "the model".
5. It does not read the concentration data: replacing the five concentrations by random values of the same magnitude flips 17 (merged) and 18 (adapters) of 11860 decisions (0.15 %), accuracy unchanged (+0.02 / +0.04 points), spread over `analysis` (7 and 9 rows of 593), `auc_method`, `compare_pair`, `route`, `is_not_available` (1) and three `asked_*` (at most 3 rows each).
   Removing the table does change answers (88 / 74 flips, `analysis` -5.2 / -2.2 points, `asked_cmax` +1.2 / +2.4 points): what it reads is the presence and header of a table, not its numbers. For these 20 questions that is correct, nothing depends on the values; it also means the ablation cannot show whether the model *could* use the data
   for a question that needs it, and no such question exists in the closed set.

## Files

`train.log`, `train_summary.json`; `predict-*.log`; `unsloth-qwen35-0.8b-d01-v2-{merged,adapters}-<set>-cuda.{json,md}` (one entry per row and question); `tables-*.md` (per-question tables with the rules column, `set_tables.py`);
`ood74/` (predictions on the 74 rows); `v1/` (v1 model on the 74 old rows); `diag-adapters-4bit/`; `ablation-*.{md,json}`; `eval_ood*.log`, `harness*.log`, `ablation*.log`. Model folders are git-ignored.
