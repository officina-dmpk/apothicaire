"""Decider of the decision harness backed by a model trained with decision/train_unsloth.py (D-01, step 5).

  python decision/run_harness.py --decider decider_unsloth:decide

`decide(state, questions) -> {question: label}` as decision/harness.py expects it. The merged model is loaded once (first call), on cuda,
from $D01_MODEL (default decision/models/qwen35-0.8b-d01/merged; `eval_ood.py --model DIR` and `ablation.py --model DIR` set it; a folder
that holds a `merged` folder is accepted for it, `.../adapters` is loaded as it was trained: LoRA + head on the 4-bit base). One FastDecisionModel.predict call answers every question of the state.
A choice answer is its likeliest option, a noul answer is "true" when P(true) >= 0.5, as in decision/predict_unsloth.py.

`decide.last_info` holds, for the last call, {question: {"label", "confidence", "probabilities"}} (confidence = probability of the label
chosen) and the seconds of the call: the harness copies it into the run JSON (decisions[i]["model_info"]). `decide.summary()` gives the
calls, the seconds and the GPU memory of the whole run (run_harness.py writes it to decider_summary.json).
"""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MODEL = os.path.join(HERE, "models", "qwen35-0.8b-d01", "merged")

_M = {}          # model, tokenizer, load seconds (loaded once)
_STATS = {"calls": 0, "seconds": 0.0}


def model_path(env=None):
    """The model folder: $D01_MODEL (a folder written by train_unsloth.py: `merged` or `adapters` itself, or its parent, which means `merged`)
    or the default."""
    path = (os.environ if env is None else env).get("D01_MODEL") or DEFAULT_MODEL
    merged = os.path.join(path, "merged")
    return merged if os.path.isdir(merged) else path


def is_adapters(path):
    """True for the `adapters` folder of train_unsloth.py (LoRA + head, to be loaded on the 4-bit base, as the model was trained)."""
    return os.path.basename(os.path.normpath(path)) == "adapters"


def model_label(path=None):
    """Short name of a model folder, used for the run folder of eval_ood.py: `qwen35-0.8b` for the default (Step 3 model), else the name
    of the folder that holds `merged` (`decision/models/<name>/merged` -> `<name>`) or `adapters` (-> `<name>-adapters`), so two models
    never write to the same run folder."""
    path = os.path.normpath(path or model_path())
    if path == os.path.normpath(DEFAULT_MODEL): return "qwen35-0.8b"
    parts = path.split(os.sep)
    if parts[-1] == "adapters" and len(parts) > 1: return parts[-2] + "-adapters"
    return parts[-2] if parts[-1] == "merged" and len(parts) > 1 else parts[-1]


def labels_of(questions, answers):
    """({question: label}, {question: {"label", "confidence", "probabilities"}}) from the answers of FastDecisionModel.predict."""
    labels, info = {}, {}
    for q, spec in questions.items():
        a = answers[q]
        if spec["type"] == "noul":
            p = float(a["noul"])
            probs = {"false": 1.0 - p, "true": p}
            label = "true" if p >= 0.5 else "false"
        else:
            probs = {k: float(v) for k, v in a["probabilities"].items()}
            label = a.get("choice") or max(probs, key=probs.get)
        labels[q] = label
        info[q] = {"label": label, "confidence": round(probs[label], 4), "probabilities": {k: round(v, 4) for k, v in probs.items()}}
    return labels, info


def _load():
    if _M: return
    import torch
    from unsloth import FastDecisionModel
    path = model_path()
    t0 = time.perf_counter()
    model, tokenizer = FastDecisionModel.from_pretrained(path, max_seq_length=2560, **({"load_in_4bit": True} if is_adapters(path) else {}))
    FastDecisionModel.for_inference(model)
    torch.cuda.reset_peak_memory_stats()
    _M.update(model=model, tokenizer=tokenizer, load_s=time.perf_counter() - t0, path=path)


def decide(state, questions):
    import torch
    from unsloth import FastDecisionModel
    _load()
    text = json.dumps(state, ensure_ascii=False, sort_keys=True)       # the form of the `state` column of the dataset
    t0 = time.perf_counter()
    with torch.inference_mode():
        answers = FastDecisionModel.predict(_M["model"], _M["tokenizer"], text, questions)
    dt = time.perf_counter() - t0
    labels, info = labels_of(questions, answers)
    _STATS["calls"] += 1; _STATS["seconds"] += dt
    decide.last_info = {"seconds": round(dt, 4), "answers": info}
    return labels


def summary():
    import torch
    from subprocess import run
    out = {"model": _M.get("path"), "load_s": round(_M.get("load_s", 0.0), 1), "decide_calls": _STATS["calls"],
           "model_seconds_total": round(_STATS["seconds"], 2),
           "model_seconds_per_call": round(_STATS["seconds"] / max(1, _STATS["calls"]), 4),
           "torch_peak_allocated_mib": round(torch.cuda.max_memory_allocated() / 2**20)}
    try:
        used = run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=20)
        out["nvidia_smi_used_mib_at_end"] = int(used.stdout.strip().splitlines()[0])
    except Exception:
        pass
    return out


decide.name = model_label()
decide.get_name = lambda: model_label()      # read by eval_ood.load_decider after $D01_MODEL is set
decide.last_info = None
decide.summary = summary
