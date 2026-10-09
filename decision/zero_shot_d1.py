#!/usr/bin/env python
"""Zero-shot baseline of the Liquid AI d1 decision models on the typed-decisions rows (D-01, step 2). No training.

  python decision/zero_shot_d1.py --model d1-omni-600M --split heldout [--limit N] [--device cuda|cpu] [--date YYYY-MM-DD]

Needs the virtual environment of decision/requirements-d1.txt (torch, transformers>=5.15; the model ships its own code, hence
trust_remote_code=True). Each row (decision/data/<split>.jsonl) is one call of the model card's API, `model.system_one(state, questions)`:
the state is the row's JSON state as text, the questions are the row's questions as they are (type, instructions, criteria; a `noul`
question keeps its false/true criteria). One forward pass answers the seven questions of the row. Writes
decision/runs/<date>/d1-<model>-<split>.json (one entry per row and question: gold, predicted label, probabilities; `-limit<N>` in the
name for a smoke run) and rebuilds decision/runs/<date>/report.md from every run file of that folder: accuracy per question and overall,
confusion of `analysis` and `parameter_asked`, calibration table (10 bins of the probability of the chosen label), wall time per row.

A `noul` answer is P(true); it is turned into probabilities {false: 1-p, true: p} and the label is the likelier side.
"""
import argparse, collections, datetime, glob, json, os, platform, statistics, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
RUNS = os.path.join(HERE, "runs")
HF_IDS = {"d1-omni-600M": "LiquidAI/d1-omni-600M", "d1-3B": "LiquidAI/d1-3B"}
CONFUSION_OF = ("analysis", "parameter_asked")
N_BINS = 10


# ---------------------------------------------------------------- format conversion
def load_rows(path, limit=None, stride=1):
    """Rows of a jsonl file: every `stride`-th row (the files are ordered by exercise, so a stride spreads a short run over all the
    exercises), at most `limit` of them."""
    rows = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if not line.strip() or i % stride: continue
            rows.append(json.loads(line))
            if limit and len(rows) >= limit: break
    return rows


def to_call(row):
    """(state text, questions dict, gold labels dict) of one dataset row, in the format of `model.system_one`."""
    state = json.dumps(json.loads(row["state"]), ensure_ascii=False, sort_keys=True)
    questions = json.loads(row["questions"])
    call = {}
    for name, q in questions.items():
        item = {"type": q["type"], "instructions": q["instructions"]}
        if q.get("criteria") is not None: item["criteria"] = q["criteria"]
        call[name] = item
    gold = {name: g["label"] for name, g in json.loads(row["gold"]).items()}
    return state, call, gold


def normalise_answer(question, answer):
    """{label, probs} from a d1 answer: `choice` has the label and the probabilities; `noul` is P(true) alone."""
    if question["type"] == "choice":
        probs = {k: float(v) for k, v in answer["probabilities"].items()}
        label = answer.get("choice") or max(probs, key=probs.get)
    elif question["type"] == "noul":
        p = float(answer["noul"])
        probs = {"false": 1.0 - p, "true": p}
        label = "true" if p >= 0.5 else "false"
    else:
        raise ValueError("question type not handled in the closed set: %r" % question["type"])
    return {"label": label, "probs": probs}


def predict_rows(predict, rows, progress=None):
    """Run `predict(state_text, questions) -> {"answers": {...}}` on each row; per row timing in seconds."""
    out = []
    for i, row in enumerate(rows):
        state, call, gold = to_call(row)
        t0 = time.perf_counter()
        res = predict(state, call)
        dt = time.perf_counter() - t0
        answers = res["answers"] if "answers" in res else res
        preds = {name: normalise_answer(call[name], answers[name]) for name in call}
        out.append({"id": row["id"], "seconds": dt, "gold": gold, "pred": preds})
        if progress and (i + 1) % progress == 0: print("  %d/%d rows, %.1f ms/row" % (i + 1, len(rows), 1000 * dt), flush=True)
    return out


# ---------------------------------------------------------------- metrics
def accuracy(results):
    """({question: (correct, total)}, (correct, total) overall)."""
    per = collections.defaultdict(lambda: [0, 0])
    for r in results:
        for q, g in r["gold"].items():
            per[q][1] += 1
            per[q][0] += r["pred"][q]["label"] == g
    tot = [sum(v[0] for v in per.values()), sum(v[1] for v in per.values())]
    return {q: tuple(v) for q, v in per.items()}, tuple(tot)


def majority(results):
    """{question: (count of the most frequent gold label, total)}: the accuracy of always answering that label."""
    c = collections.defaultdict(collections.Counter)
    for r in results:
        for q, g in r["gold"].items(): c[q][g] += 1
    return {q: (max(v.values()), sum(v.values())) for q, v in c.items()}


def confusion(results, question):
    """{gold label: {predicted label: count}}."""
    m = collections.defaultdict(collections.Counter)
    for r in results:
        if question in r["gold"]: m[r["gold"][question]][r["pred"][question]["label"]] += 1
    return {g: dict(c) for g, c in m.items()}


def bin_index(p, n_bins=N_BINS):
    return min(int(p * n_bins), n_bins - 1)


def calibration(results, questions=None, n_bins=N_BINS):
    """Reliability table of the probability of the chosen label: one entry per bin
    {lo, hi, n, mean_conf, acc}; mean_conf and acc are None for an empty bin. Also the expected calibration error."""
    bins = [[0, 0.0, 0] for _ in range(n_bins)]
    total = 0
    for r in results:
        for q, g in r["gold"].items():
            if questions is not None and q not in questions: continue
            pr = r["pred"][q]
            b = bins[bin_index(pr["probs"][pr["label"]], n_bins)]
            b[0] += 1; b[1] += pr["probs"][pr["label"]]; b[2] += pr["label"] == g
            total += 1
    table, ece = [], 0.0
    for i, (n, sc, sa) in enumerate(bins):
        table.append({"lo": i / n_bins, "hi": (i + 1) / n_bins, "n": n,
                      "mean_conf": sc / n if n else None, "acc": sa / n if n else None})
        if n: ece += n / total * abs(sc / n - sa / n)
    return table, (ece if total else None)


def timing(results):
    s = sorted(r["seconds"] for r in results)
    if not s: return {"mean_ms": None, "median_ms": None, "p95_ms": None}
    return {"mean_ms": 1000 * statistics.fmean(s), "median_ms": 1000 * statistics.median(s),
            "p95_ms": 1000 * s[min(len(s) - 1, int(0.95 * len(s)))]}


# ---------------------------------------------------------------- report
def pct(a, b): return "%.1f %%" % (100 * a / b) if b else "n/a"


def md_table(header, rows):
    return "\n".join(["| " + " | ".join(header) + " |", "|" + "---|" * len(header)] +
                     ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def run_title(meta):
    sub = ""
    if meta.get("limit"): sub = ", %d rows" % meta["n_rows"] if meta.get("stride", 1) > 1 else ", first %d rows" % meta["limit"]
    if meta.get("stride", 1) > 1: sub += " (every %dth)" % meta["stride"]
    return "%s, %s%s" % (meta["model"], meta["split"], sub)


def run_section(run):
    meta, res = run["meta"], run["rows"]
    per, tot = accuracy(res)
    names = list(per)
    ece_all = calibration(res)[1]
    L = ["## " + run_title(meta), ""]
    L.append("Rows %d, questions %d, device %s, dtype %s, model load %.1f s, inference wall %.1f s (after %d untimed warm-up rows)." %
             (meta["n_rows"], tot[1], meta["device"], meta["dtype"], meta["load_s"], meta["wall_s"], meta.get("warmup_rows", 0)))
    t = timing(res)
    L.append("Time per row (one call, %d questions): mean %.1f ms, median %.1f ms, p95 %.1f ms. VRAM: %s." %
             (round(tot[1] / meta["n_rows"]), t["mean_ms"], t["median_ms"], t["p95_ms"], meta.get("vram_text", "n/a")))
    L += ["", "### Accuracy per question", ""]
    maj = majority(res)
    maj_tot = (sum(v[0] for v in maj.values()), sum(v[1] for v in maj.values()))
    L.append(md_table(["question", "correct", "total", "accuracy", "always-majority", "ECE"],
                      [(q, per[q][0], per[q][1], pct(*per[q]), pct(*maj[q]), "%.3f" % calibration(res, {q})[1]) for q in names]
                      + [("**overall**", tot[0], tot[1], "**%s**" % pct(*tot), pct(*maj_tot), "%.3f" % ece_all)]))
    for q in CONFUSION_OF:
        if q not in per: continue
        cm = confusion(res, q)
        gold_labels = sorted(cm)
        pred_labels = sorted({p for c in cm.values() for p in c} | set(gold_labels))
        L += ["", "### Confusion: %s (rows = gold, columns = predicted)" % q, ""]
        L.append(md_table(["gold \\ pred"] + pred_labels + ["total", "recall"],
                          [[g] + [cm[g].get(p, "") for p in pred_labels] + [sum(cm[g].values()), pct(cm[g].get(g, 0), sum(cm[g].values()))]
                           for g in gold_labels]))
    table, ece = calibration(res)
    L += ["", "### Calibration (all questions; probability of the chosen label vs observed accuracy)", ""]
    L.append(md_table(["bin", "count", "mean predicted", "observed accuracy"],
                      [("[%.1f, %.1f%s" % (b["lo"], b["hi"], "]" if b["hi"] >= 1 else ")"), b["n"],
                        "%.3f" % b["mean_conf"] if b["n"] else "-", "%.3f" % b["acc"] if b["n"] else "-") for b in table]))
    L += ["", "Expected calibration error: %s." % ("%.3f" % ece if ece is not None else "n/a")]
    return "\n".join(L)


def run_files(folder):
    runs = []
    for p in sorted(glob.glob(os.path.join(folder, "d1-*-*.json"))):
        with open(p, encoding="utf-8") as f: runs.append(json.load(f))
    # full runs first, smoke runs last
    runs.sort(key=lambda r: (bool(r["meta"].get("limit")) and r["meta"]["n_rows"] < 50,  # smoke runs last
                             r["meta"]["split"] != "heldout", r["meta"]["model"]))
    return runs


def summary_table(runs):
    rows = []
    for r in runs:
        per, tot = accuracy(r["rows"])
        rows.append((run_title(r["meta"]), r["meta"]["n_rows"], pct(*tot), "%.3f" % calibration(r["rows"])[1],
                     "%.1f" % timing(r["rows"])["mean_ms"], r["meta"]["device"] + "/" + r["meta"]["dtype"]))
    return md_table(["run", "rows", "overall accuracy", "ECE", "ms per row", "device/dtype"], rows)


def write_report(folder):
    runs = run_files(folder)
    if not runs: return None
    m = runs[0]["meta"]
    L = ["# Zero-shot baseline of d1 on the typed-decisions rows (D-01, step 2)", "",
         "No training. `decision/zero_shot_d1.py`, the model card's `system_one(state, questions)`, one call per row (seven questions: five `choice`, two `noul`).",
         "Environment: python %s, torch %s, transformers %s, GPU: %s." % (m["python"], m["torch"], m["transformers"],
                                                          ", ".join(sorted({r["meta"].get("gpu") or "none" for r in runs}))),
         "Gold is one-hot (the truth is known), so calibration is measured against a certain label. `noul` probabilities come from P(true).", "",
         "## Summary", "", summary_table(runs), "", "\n\n".join(run_section(r) for r in runs), ""]
    notes = os.path.join(folder, "notes.md")  # hand-written remarks of the folder (what failed, what was run), appended as is
    if os.path.exists(notes):
        with open(notes, encoding="utf-8") as f: L += [f.read().rstrip(), ""]
    path = os.path.join(folder, "report.md")
    with open(path, "w", encoding="utf-8", newline="\n") as f: f.write("\n".join(L))
    return path


# ---------------------------------------------------------------- model
def nvidia_smi_used():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=20).stdout.strip().splitlines()[0]
        used, total = (int(x) for x in out.split(","))
        return used, total
    except Exception:
        return None, None


def load_model(name, device):
    import torch
    from transformers import AutoModel
    dtype = torch.float32 if device == "cpu" else (torch.float16 if name == "d1-omni-600M" else torch.bfloat16)  # as in the model cards
    model = AutoModel.from_pretrained(HF_IDS[name], trust_remote_code=True, dtype=dtype).to(device)
    model.eval()
    return model, str(dtype).replace("torch.", "")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--model", choices=sorted(HF_IDS), required=True)
    ap.add_argument("--split", choices=["heldout", "bench", "train"], default="heldout")
    ap.add_argument("--limit", type=int, default=None, help="first N rows only (smoke run; the file name gets -limitN)")
    ap.add_argument("--stride", type=int, default=1, help="take every STRIDE-th row (spreads a --limit run over all the exercises; -strideK in the file name)")
    ap.add_argument("--device", choices=["cpu", "cuda"], default="cuda")
    ap.add_argument("--date", default=datetime.date.today().isoformat(), help="run folder decision/runs/<date>")
    ap.add_argument("--warmup", type=int, default=2, help="rows run first and not timed")
    a = ap.parse_args(argv)

    import torch, transformers
    rows = load_rows(os.path.join(DATA, a.split + ".jsonl"), a.limit, a.stride)
    if not rows: sys.exit("no rows in %s" % a.split)
    smi_before = nvidia_smi_used()[0]
    t0 = time.perf_counter()
    model, dtype = load_model(a.model, a.device)
    load_s = time.perf_counter() - t0
    smi_loaded = nvidia_smi_used()[0]
    if a.device == "cuda": torch.cuda.reset_peak_memory_stats()
    predict = lambda state, qs: model.system_one(state, qs)
    with torch.inference_mode():
        for row in rows[:a.warmup]:  # kernel selection on the first calls is not part of the per-row time
            s, c, _ = to_call(row); predict(s, c)
        t1 = time.perf_counter()
        res = predict_rows(predict, rows, progress=100)
        wall_s = time.perf_counter() - t1
    smi_after, smi_total = nvidia_smi_used()
    meta = {"model": a.model, "hf_id": HF_IDS[a.model], "split": a.split, "limit": a.limit, "stride": a.stride, "n_rows": len(rows), "device": a.device,
            "dtype": dtype, "load_s": load_s, "wall_s": wall_s, "warmup_rows": a.warmup,
            "python": platform.python_version(), "torch": torch.__version__, "transformers": transformers.__version__,
            "gpu": torch.cuda.get_device_name(0) if a.device == "cuda" else None,
            "started": datetime.datetime.now().isoformat(timespec="seconds"),
            "vram_nvidia_smi_mib": {"before_load": smi_before, "after_load": smi_loaded, "after_run": smi_after, "total": smi_total},
            "vram_torch_peak_mib": torch.cuda.max_memory_allocated() / 2**20 if a.device == "cuda" else None}
    if a.device == "cuda":
        meta["vram_text"] = "nvidia-smi used %s MiB before load, %s after load, %s after the run (of %s); torch peak allocated %.0f MiB" % (
            smi_before, smi_loaded, smi_after, smi_total, meta["vram_torch_peak_mib"])
    else:
        meta["vram_text"] = "none (cpu)"
    folder = os.path.join(RUNS, a.date)
    os.makedirs(folder, exist_ok=True)
    name = "d1-%s-%s%s%s.json" % (a.model.replace("d1-", ""), a.split, ("-limit%d" % a.limit) if a.limit else "",
                                  ("-stride%d" % a.stride) if a.stride > 1 else "")
    with open(os.path.join(folder, name), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"meta": meta, "rows": res}, f, ensure_ascii=False)
    print("wrote", os.path.join(folder, name))
    per, tot = accuracy(res)
    print("overall %d/%d = %s; mean %.1f ms/row" % (tot[0], tot[1], pct(*tot), timing(res)["mean_ms"]))
    print("report:", write_report(folder))


if __name__ == "__main__":
    main()
