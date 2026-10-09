#!/usr/bin/env python
"""Predict with a decision model trained by decision/train_unsloth.py and score it against the gold labels (D-01, step 3).

  python decision/predict_unsloth.py --model decision/models/<name>/merged --split heldout [--limit N] [--stride K]
                                     [--device cuda|cpu] [--load-in-4bit] [--date YYYY-MM-DD] [--out-dir DIR]

--model is a folder written by train_unsloth.py: `merged` (16-bit, runs on cuda or cpu) or `adapters` (LoRA + head on the base model,
needs the base model in the Hugging Face cache or online). --split is a name in decision/data (heldout, bench, train) or a path to a jsonl
file in the typed-decisions format. One FastDecisionModel.predict call per row answers every question the row declares.

Writes <out-dir>/unsloth-<name>-<split>[-limitN][-strideK][-<device>].json (one entry per row and question: gold, label, probabilities,
seconds) and the same name with .md: accuracy per question against the always-majority baseline, confusion of `analysis` and
`parameter_asked`, 10-bin calibration table. The metric and report functions are those of decision/zero_shot_d1.py (same tables, so the
runs read side by side). Default out-dir: decision/runs/<date>.
"""
import argparse, datetime, json, os, platform, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import zero_shot_d1 as z  # noqa: E402  (load_rows, to_call, normalise_answer, predict_rows, accuracy, calibration, run_section ...)

CONFUSION_OF = ("analysis", "route", "auc_method", "compare_pair", "is_not_available")  # confusion tables of the report (set on z in main)


def split_path(split):
    """decision/data/<split>.jsonl for a split name, the path itself for an existing file."""
    return split if os.path.isfile(split) else os.path.join(z.DATA, split + ".jsonl")


def model_name(path):
    """`<run>-<kind>` from decision/models/<run>/<kind> (kind is merged or adapters)."""
    parts = os.path.normpath(path).split(os.sep)
    return "-".join(parts[-2:]) if parts[-1] in ("merged", "adapters") and len(parts) > 1 else parts[-1]


def run_name(name, split, limit, stride, device):
    split = os.path.splitext(os.path.basename(split))[0]
    return "unsloth-%s-%s%s%s-%s" % (name, split, ("-limit%d" % limit) if limit else "", ("-stride%d" % stride) if stride > 1 else "", device)


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--model", required=True, help="folder saved by train_unsloth.py (merged or adapters)")
    ap.add_argument("--split", default="heldout", help="heldout, bench, train (decision/data/<split>.jsonl) or a jsonl path")
    ap.add_argument("--limit", type=int, default=None, help="first N rows (after --stride)")
    ap.add_argument("--stride", type=int, default=1, help="every STRIDE-th row (spreads a --limit run over the exercises)")
    ap.add_argument("--device", choices=["cuda", "cpu"], default="cuda")
    ap.add_argument("--load-in-4bit", action="store_true", help="4-bit weights (cuda only; adapters on the 4-bit base)")
    ap.add_argument("--max-seq-length", type=int, default=2048)
    ap.add_argument("--warmup", type=int, default=2, help="rows run first and not timed")
    ap.add_argument("--date", default=datetime.date.today().isoformat(), help="run folder decision/runs/<date>")
    ap.add_argument("--out-dir", default=None)
    return ap.parse_args(argv)


def _reference_gated_delta():
    """Unsloth swaps the Qwen3.5 gated-delta-net kernels of transformers for vendored Triton ones, which cannot read a cpu tensor
    ("Pointer argument cannot be accessed from Triton"). Put the plain PyTorch reference functions back in the Qwen3.5 modeling modules."""
    import importlib, inspect
    for pkg in ("qwen3_5", "qwen3_5_moe"):
        try: mod = importlib.import_module("transformers.models.%s.modeling_%s" % (pkg, pkg))
        except ImportError: continue
        for fn in ("torch_chunk_gated_delta_rule", "torch_recurrent_gated_delta_rule"):
            if hasattr(mod, fn): setattr(mod, fn, inspect.unwrap(getattr(mod, fn)))


def load_model(path, device, load_in_4bit, max_seq_length):
    """(model, tokenizer, dtype name, device). `import unsloth` itself needs a visible GPU ("Unsloth cannot find any torch accelerator"),
    so on cpu the GPU stays visible for the import and `torch.cuda.is_available` is switched off just before the load: Unsloth then takes
    its own CPU path (plain transformers backbone in float32, no 4-bit). The merged folder is the one to load on cpu."""
    import torch
    from unsloth import FastDecisionModel
    if device == "cpu":
        torch.cuda.is_available = lambda: False
        _reference_gated_delta()
    model, tokenizer = FastDecisionModel.from_pretrained(path, max_seq_length=max_seq_length, load_in_4bit=load_in_4bit)
    FastDecisionModel.for_inference(model)
    p = next(model.parameters())
    return model, tokenizer, str(p.dtype).replace("torch.", ""), str(p.device)


def baseline_section(res):
    """Markdown: the questions whose accuracy is at or below the always-majority baseline."""
    per, _ = z.accuracy(res); maj = z.majority(res)
    low = sorted((q for q in per if per[q][0] <= maj[q][0]), key=lambda q: per[q][0] / per[q][1] - maj[q][0] / maj[q][1])
    L = ["### Questions at or below the always-majority baseline", ""]
    if not low: return "\n".join(L + ["None: every question is above its baseline.", ""])
    L.append(z.md_table(["question", "accuracy", "always-majority", "difference (points)"],
                        [(q, z.pct(*per[q]), z.pct(*maj[q]), "%+.1f" % (100 * (per[q][0] / per[q][1] - maj[q][0] / maj[q][1]))) for q in low]))
    return "\n".join(L + [""])


def main(argv=None):
    z.CONFUSION_OF = CONFUSION_OF       # here, not at import: the tests of zero_shot_d1 import this module in the same process
    a = parse_args(argv)
    rows = z.load_rows(split_path(a.split), a.limit, a.stride)
    if not rows: sys.exit("no rows in %s" % a.split)
    smi_before = z.nvidia_smi_used()[0] if a.device == "cuda" else None
    t0 = time.perf_counter()
    model, tokenizer, dtype, where = load_model(a.model, a.device, a.load_in_4bit, a.max_seq_length)
    load_s = time.perf_counter() - t0
    import torch
    from unsloth import FastDecisionModel
    if a.device == "cuda": torch.cuda.reset_peak_memory_stats()
    predict = lambda state, qs: FastDecisionModel.predict(model, tokenizer, state, qs)
    with torch.inference_mode():
        for row in rows[:a.warmup]:  # kernel selection / compilation on the first calls is not part of the per-row time
            s, c, _ = z.to_call(row); predict(s, c)
        t1 = time.perf_counter()
        res = z.predict_rows(predict, rows, progress=100)
        wall_s = time.perf_counter() - t1
    smi_after = z.nvidia_smi_used()[0] if a.device == "cuda" else None
    name = model_name(a.model)
    meta = {"model": name, "path": os.path.abspath(a.model), "split": os.path.splitext(os.path.basename(a.split))[0], "limit": a.limit,
            "stride": a.stride, "n_rows": len(rows), "device": a.device, "dtype": dtype, "load_s": load_s, "wall_s": wall_s,
            "warmup_rows": a.warmup, "python": platform.python_version(), "torch": torch.__version__,
            "gpu": torch.cuda.get_device_name(0) if a.device == "cuda" else None,
            "started": datetime.datetime.now().isoformat(timespec="seconds"), "model_device": where}
    if a.device == "cuda":
        meta["vram_text"] = "nvidia-smi used %s MiB before load, %s after the run; torch peak allocated %.0f MiB" % (
            smi_before, smi_after, torch.cuda.max_memory_allocated() / 2**20)
    else:
        meta["vram_text"] = "none (cpu)"
    folder = a.out_dir or os.path.join(z.RUNS, a.date)
    os.makedirs(folder, exist_ok=True)
    base = os.path.join(folder, run_name(name, a.split, a.limit, a.stride, a.device))
    with open(base + ".json", "w", encoding="utf-8", newline="\n") as f:
        json.dump({"meta": meta, "rows": res}, f, ensure_ascii=False)
    run = {"meta": meta, "rows": res}
    head = ["# %s on %s (Unsloth decision model)" % (name, meta["split"]), "",
            "`decision/predict_unsloth.py`, `FastDecisionModel.predict`, one call per row. Gold is one-hot, so calibration is measured against a "
            "certain label; `noul` probabilities are P(true). Python %s, torch %s." % (meta["python"], meta["torch"]), "",
            z.summary_table([run]), ""]
    with open(base + ".md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(head) + "\n" + z.run_section(run) + "\n\n" + baseline_section(res) + "\n")
    per, tot = z.accuracy(res)
    print("wrote", base + ".json / .md")
    print("overall %d/%d = %s; ECE %.3f; mean %.1f ms/row" % (tot[0], tot[1], z.pct(*tot), z.calibration(res)[1], z.timing(res)["mean_ms"]))
    for q in sorted(per): print("  %-24s %s" % (q, z.pct(*per[q])))


if __name__ == "__main__":
    main()
