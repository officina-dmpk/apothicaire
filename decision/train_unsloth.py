#!/usr/bin/env python
"""Fine-tune a decision model with Unsloth on the typed-decisions rows of decision/data (D-01, step 3).

  python decision/train_unsloth.py [--base unsloth/Qwen3.5-0.8B] [--epochs 2] [--batch-size 8] [--grad-accum 4] [--lr 2e-4]
                                   [--limit N] [--eval-limit N] [--out decision/models/<name>]

Recipe of https://unsloth.ai/docs/basics/train-your-own-decision-model-with-unsloth: FastDecisionModel.from_pretrained (4-bit) ->
get_peft_model (LoRA) -> build_dataset -> DecisionTrainer -> calibrate -> save_pretrained (adapters + head) and save_pretrained_merged.
Training rows: decision/data/train.jsonl; evaluation and calibration rows: decision/data/heldout.jsonl (whole exercises never seen in
training, our own split instead of FastDecisionModel.split_holdout). The rows are read as they are: the questions a row declares are the
questions the model is trained on, so the question set of the dataset can change without touching this file.

--limit / --eval-limit keep N rows spread evenly over the file (the files are ordered by exercise; a prefix would cover 3 exercises).
Writes <out>/train_summary.json (versions, times, VRAM peak, build_dataset report, metrics).
"""
import argparse, datetime, json, os, platform, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
MODELS = os.path.join(HERE, "models")
DEFAULT_BASE = "unsloth/Qwen3.5-0.8B"


# ---------------------------------------------------------------- data (no torch needed)
def read_jsonl(path):
    """The rows of a jsonl file, as dicts, in file order."""
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def spread(rows, limit=None):
    """At most `limit` rows, evenly spaced over `rows` (deterministic); all of them when limit is None or not smaller than len(rows)."""
    if not limit or limit >= len(rows): return list(rows)
    return [rows[i * len(rows) // limit] for i in range(limit)]


def to_dataset(rows):
    """Hugging Face `datasets.Dataset` of typed-decisions rows (state, questions and gold stay JSON text, as in the Hub dataset)."""
    from datasets import Dataset
    keep = ["id", "workflow", "split", "state", "questions", "gold", "n_questions"]
    return Dataset.from_list([{k: r[k] for k in keep if k in r} for r in rows])


def load_split(name, limit=None, data_dir=DATA):
    """Dataset of decision/data/<name>.jsonl (`name` is train, heldout or bench), spread down to `limit` rows."""
    return to_dataset(spread(read_jsonl(os.path.join(data_dir, name + ".jsonl")), limit))


def question_names(dataset):
    """Sorted names of every question declared by the rows of a dataset."""
    names = set()
    for row in dataset: names |= set(json.loads(row["questions"]))
    return sorted(names)


# ---------------------------------------------------------------- arguments
def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", default=DEFAULT_BASE, help="base model (Hub id or local folder), default %(default)s")
    ap.add_argument("--train", default="train", help="decision/data/<name>.jsonl used for training")
    ap.add_argument("--heldout", default="heldout", help="decision/data/<name>.jsonl used for evaluation and calibration")
    ap.add_argument("--limit", type=int, default=None, help="train on N rows spread over the file (smoke run)")
    ap.add_argument("--eval-limit", type=int, default=None, help="evaluate and calibrate on N held-out rows spread over the file")
    ap.add_argument("--epochs", type=float, default=2.0)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--grad-accum", type=int, default=4)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--head-lr", type=float, default=None, help="learning rate of the decision head (Unsloth default 1e-4)")
    ap.add_argument("--max-steps", type=int, default=-1, help="stop after N optimizer steps (overrides --epochs)")
    ap.add_argument("--max-seq-length", type=int, default=2048)
    ap.add_argument("--lora-r", type=int, default=16)
    ap.add_argument("--no-4bit", action="store_true", help="load the base model in 16 bit instead of 4 bit")
    ap.add_argument("--seed", type=int, default=3407)
    ap.add_argument("--out", default=None, help="model folder, default decision/models/<base name>-decisions")
    a = ap.parse_args(argv)
    if a.out is None: a.out = os.path.join(MODELS, a.base.rstrip("/").split("/")[-1].lower() + "-decisions")
    return a


# ---------------------------------------------------------------- GPU
def nvidia_smi_used():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=20).stdout.strip().splitlines()[0]
        used, total = (int(x) for x in out.split(","))
        return used, total
    except Exception:
        return None, None


class SmiPeak:
    """Highest `nvidia-smi` memory.used seen while it runs (sampled every 2 s in a thread): the torch allocator figure misses the
    CUDA context and the cache, nvidia-smi sees the whole process (and any other process on the GPU)."""
    def __init__(self):
        import threading
        self.peak, self._stop, self._t = 0, threading.Event(), None
        self._threading = threading

    def __enter__(self):
        def loop():
            while not self._stop.is_set():
                used = nvidia_smi_used()[0]
                if used: self.peak = max(self.peak, used)
                self._stop.wait(2.0)
        self._t = self._threading.Thread(target=loop, daemon=True); self._t.start()
        return self

    def __exit__(self, *exc):
        self._stop.set(); self._t.join()


# ---------------------------------------------------------------- main
def main(argv=None):
    a = parse_args(argv)
    t_start = time.perf_counter()
    import torch
    from unsloth import FastDecisionModel, DecisionTrainer, is_bfloat16_supported  # unsloth first: it patches transformers
    import transformers, unsloth
    from transformers import TrainingArguments

    train_ds, held_ds = load_split(a.train, a.limit), load_split(a.heldout, a.eval_limit)
    print("train rows %d, held-out rows %d, questions %s" % (len(train_ds), len(held_ds), question_names(train_ds)), flush=True)

    smi_before = nvidia_smi_used()[0]
    with SmiPeak() as smi:
        t0 = time.perf_counter()
        model, tokenizer = FastDecisionModel.from_pretrained(a.base, max_seq_length=a.max_seq_length, load_in_4bit=not a.no_4bit,
                                                             random_state=a.seed)
        model = FastDecisionModel.get_peft_model(model, r=a.lora_r, lora_alpha=a.lora_r, lora_dropout=0,
                                                 use_gradient_checkpointing="unsloth", random_state=a.seed)
        load_s = time.perf_counter() - t0

        train_items, train_report = FastDecisionModel.build_dataset(train_ds, tokenizer, model)
        held_items, held_report = FastDecisionModel.build_dataset(held_ds, tokenizer, model)
        print("build_dataset train:", train_report, flush=True)
        print("build_dataset held-out:", held_report, flush=True)

        os.makedirs(a.out, exist_ok=True)
        bf16 = is_bfloat16_supported()
        args = TrainingArguments(
            per_device_train_batch_size=a.batch_size, per_device_eval_batch_size=a.batch_size,
            gradient_accumulation_steps=a.grad_accum, num_train_epochs=a.epochs, max_steps=a.max_steps,
            learning_rate=a.lr, lr_scheduler_type="cosine", warmup_steps=10, weight_decay=0.01,
            bf16=bf16, fp16=not bf16, eval_strategy="epoch", save_strategy="no", logging_steps=10,
            output_dir=os.path.join(a.out, "trainer"), report_to="none", seed=a.seed)
        trainer = DecisionTrainer(model=model, processing_class=tokenizer, train_dataset=train_items, eval_dataset=held_items,
                                  args=args, head_learning_rate=a.head_lr)
        torch.cuda.reset_peak_memory_stats()
        t1 = time.perf_counter()
        result = trainer.train()
        train_s = time.perf_counter() - t1
        train_peak = torch.cuda.max_memory_allocated() / 2**20

        t2 = time.perf_counter()
        metrics = FastDecisionModel.calibrate(model, tokenizer, held_items)
        calibrate_s = time.perf_counter() - t2
        print("calibrate on held-out:", metrics, flush=True)

        t3 = time.perf_counter()
        model.save_pretrained(os.path.join(a.out, "adapters"))
        model.save_pretrained_merged(os.path.join(a.out, "merged"))
        save_s = time.perf_counter() - t3
    summary = {
        "date": datetime.datetime.now().isoformat(timespec="seconds"), "args": vars(a),
        "versions": {"python": platform.python_version(), "torch": torch.__version__, "transformers": transformers.__version__,
                     "unsloth": getattr(unsloth, "__version__", None), "gpu": torch.cuda.get_device_name(0)},
        "rows": {"train": len(train_ds), "heldout": len(held_ds)},
        "questions": question_names(train_ds),
        "build_dataset": {"train": train_report, "heldout": held_report},
        "items": {"train": len(train_items), "heldout": len(held_items)},
        "train_metrics": dict(result.metrics),
        "log_history": trainer.state.log_history,
        "calibrate": metrics,
        "seconds": {"load": load_s, "train": train_s, "calibrate": calibrate_s, "save": save_s, "total": time.perf_counter() - t_start},
        "vram_mib": {"torch_peak_allocated_train": train_peak, "torch_peak_allocated_all": torch.cuda.max_memory_allocated() / 2**20,
                     "nvidia_smi_before": smi_before, "nvidia_smi_peak": smi.peak, "nvidia_smi_total": nvidia_smi_used()[1]},
    }
    with open(os.path.join(a.out, "train_summary.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1, default=str)
    print("saved", a.out, "| train %.0f s, total %.0f s, torch peak %.0f MiB, nvidia-smi peak %s MiB" % (
        train_s, summary["seconds"]["total"], train_peak, smi.peak), flush=True)


if __name__ == "__main__":
    main()
