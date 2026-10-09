#!/usr/bin/env python
"""Runs the Apothicaire benchmark: every exercise through the agent (gate in the loop), then the report.

  python bench/run_bench.py [--date YYYY-MM-DD] [--first N] [--ids ex01_iv_bolus,...] [--resume] [--report-only]

For each exercise of bench/exercises/ (sorted by id): a fresh memory folder bench/runs/<date>/<id>-data/
(git-ignored), the 8-turn script of bench/scripts.py, one record per turn; the exercise's records are written
to bench/runs/<date>/<id>.json (synthetic data, versioned). report.json and report.md are built from them.

Per turn: numbers_total / numbers_unverified (the gate) before the one regeneration and in the answer shown,
badge shown or not, tool calls (valid / invalid / failed, see classify_call), the expected numbers found
(score.score_turn), wall time, prompt tokens (first call of the turn), the taxonomy class of every unverified
number (score.classify). Metric: hallucination rate = numbers_unverified / numbers_total, with both numbers.
"""
import argparse, datetime, json, math, os, random, shutil, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
if AGENT not in sys.path: sys.path.insert(0, AGENT)
import apothicaire, gate, optchat  # noqa: E402
from bench import make_exercises as mk, scripts, score  # noqa: E402

RUNS = os.path.join(HERE, "runs")
BADGE_MARK = "\n\n⚠ "

# ---------------------------------------------------------------- tool calls
def classify_call(name, ok, text, known_tools):
    """valid: the server accepted the call and the analysis ran;
    invalid: the call itself is wrong (unknown tool, invalid_parameters, unknown_worksheet / unknown_analysis,
             any other rejection by the server);
    failed: the call was accepted but the analysis reports an error for every subject (data problem)."""
    if name not in known_tools: return "invalid"
    if not ok: return "invalid"
    if name == "nca_run":
        try:
            subj = json.loads(text)["result"]["subjects"]
            if subj and all("ok" not in s.get("outcome", {}) for s in subj): return "failed"
        except Exception: pass
    return "valid"

def elide(args, csv_text):
    a = dict(args)
    if isinstance(a.get("csv"), str):
        same = [x.strip() for x in a["csv"].strip().splitlines()] == [x.strip() for x in csv_text.strip().splitlines()]
        a["csv"] = f"<{len(a['csv'])} chars, {'identical to' if same else 'DIFFERENT from'} the exercise CSV>"
    return a

def tool_records(calls, meta, csv_text, known_tools):
    out = []
    for c in calls:
        r = {"name": c["name"], "args": elide(c["args"], csv_text), "ok": c["ok"], "shown": c["shown"][:6000],
             "status": classify_call(c["name"], c["ok"], c["text"], known_tools)}
        if not c["ok"]: r["error"] = c["text"][:240]
        if c["name"] == "data_import":
            r["csv_identical"] = r["args"].get("csv", "").startswith("<") and "identical to" in r["args"]["csv"]
        if c["name"] == "nca_run":
            a = c["args"]
            r["dose_ok"] = a.get("dose") == meta["dose"]["amount"] or (a.get("dose") is not None and float(a["dose"]) == float(meta["dose"]["amount"]))
            r["route_ok"] = a.get("route") == meta["route"]
        out.append(r)
    return out

# ---------------------------------------------------------------- one exercise
def run_exercise(ex_dir, run_dir, cfg_base=None, verbose=False, llm=None):
    """Runs the 8 turns of one exercise; returns the record (also written to <run_dir>/<id>.json)."""
    meta, csv_text = mk.load(ex_dir)
    script = scripts.build_script(meta, csv_text)
    data = os.path.join(run_dir, meta["id"] + "-data")
    if os.path.exists(data): shutil.rmtree(data)
    cfg = dict(cfg_base or optchat.CFG, data_dir=data)
    ag = apothicaire.Apothicaire(cfg=cfg)
    if llm is not None: ag.llm = llm; ag.compactor.llm = llm          # tests: a scripted model
    turns, t_ex = [], time.time()
    try:
        for k, t in enumerate(script):
            n_log, n_msgs = len(ag.tool_log), len(ag.store.log)
            rec = {"exercise": meta["id"], "turn": k + 1, "id": t["id"], "kind": t["kind"], "question": t["question"]}
            t0 = time.time()
            try:
                ans, st = ag.turn(t["question"], verbose=verbose)
            except Exception as e:                                   # a model / server failure: recorded, the exercise continues
                rec.update(error=f"{type(e).__name__}: {e}", wall_s=round(time.time() - t0, 1)); turns.append(rec)
                try: ag.wait_bg()
                except Exception: pass
                continue
            wall = time.time() - t0
            g = st.get("gate") or {}
            before, after = g.get("before", {}), g.get("after", {})
            answer = ans.split(BADGE_MARK)[0] if BADGE_MARK in ans else ans
            tool_texts, users = apothicaire.gate_context(ag.store.log, ag.mcp.tools)
            allowed = gate.allowed_numbers(tool_texts, users)
            f_before = g.get("first_findings") if g.get("regenerated") else g.get("findings", [])
            f_after = g.get("findings", [])
            cls = lambda fs, text: [{"text": f["text"], "value": f["value"], "significant_digits": f.get("significant_digits"),
                                     "position": f.get("position"), "nearest": f.get("nearest_allowed"),
                                     "class": score.classify(f, allowed, t["kind"], text)} for f in (fs or [])]
            msgs = ag.store.log[n_msgs:]
            mem_calls = sum(1 for m in msgs if m["role"] == "tool_call" for c in optchat._calls_of(m) if c["name"] in ("zoom", "read_message"))
            sc = score.score_turn(answer, t["expect"], after.get("numbers_unverified", 0))
            rec.update(
                answer=ans, wall_s=round(wall, 1), prompt_tokens=st["prompt_tokens"], rounds=st["rounds"],
                numbers_total_before=before.get("numbers_total", 0), numbers_unverified_before=before.get("numbers_unverified", 0),
                numbers_total_after=after.get("numbers_total", 0), numbers_unverified_after=after.get("numbers_unverified", 0),
                regenerated=bool(g.get("regenerated")), kept=g.get("kept"), badge=bool(f_after),
                findings_before=cls(f_before, g.get("first_answer") if g.get("regenerated") else answer), findings_after=cls(f_after, answer),
                first_answer=g.get("first_answer") if g.get("regenerated") else None,
                tool_calls=tool_records(ag.tool_log[n_log:], meta, csv_text, set(ag.mcp.tools)),
                memory_calls=mem_calls, score=sc)
            turns.append(rec)
            ag.wait_bg()                                             # compaction does not leak into the next turn's time
        tool_texts, users = apothicaire.gate_context(ag.store.log, ag.mcp.tools)
        allowed = gate.allowed_numbers(tool_texts, users)
        baseline = {str(d): score.chance_baseline(allowed, n=50, seed=meta["index"], digits=d) for d in (3, 4)}
    finally:
        ag.close()
    record = {"id": meta["id"], "family": meta["family"], "model": meta["model"], "units": meta["units"],
              "dose": meta["dose"], "blq": bool(meta.get("blq")), "wall_s": round(time.time() - t_ex, 1),
              "taxonomy_chance_baseline": baseline, "turns": turns}
    with open(os.path.join(run_dir, meta["id"] + ".json"), "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=1)
    return record

# ---------------------------------------------------------------- report
def _sum(turns, key): return sum(t.get(key, 0) or 0 for t in turns)
def _rate(u, n): return (u / n) if n else None

def cluster_interval(records, num, den, n_boot=2000, seed=0):
    """95 % percentile interval of sum(num)/sum(den) with the exercises resampled (a cluster bootstrap: the numbers
    of one conversation are not independent)."""
    per = [(sum(t.get(num, 0) or 0 for t in r["turns"]), sum(t.get(den, 0) or 0 for t in r["turns"])) for r in records]
    if len(per) < 2: return None
    rng, vals = random.Random(seed), []
    for _ in range(n_boot):
        s = [per[rng.randrange(len(per))] for _ in per]
        d = sum(x[1] for x in s)
        if d: vals.append(sum(x[0] for x in s) / d)
    vals.sort()
    return [vals[int(0.025 * len(vals))], vals[min(len(vals) - 1, int(0.975 * len(vals)))]] if vals else None

def build_report(records, meta=None):
    turns = [t for r in records for t in r["turns"]]
    ok_turns = [t for t in turns if "error" not in t]
    out = {"meta": meta or {}, "exercises": len(records), "turns": len(turns), "turns_failed": len(turns) - len(ok_turns)}
    ub, nb = _sum(ok_turns, "numbers_unverified_before"), _sum(ok_turns, "numbers_total_before")
    ua, na = _sum(ok_turns, "numbers_unverified_after"), _sum(ok_turns, "numbers_total_after")
    out["hallucination"] = {
        "before_gate": {"unverified": ub, "total": nb, "rate": _rate(ub, nb), "ci95_cluster_bootstrap": cluster_interval(records, "numbers_unverified_before", "numbers_total_before")},
        "after_gate": {"unverified": ua, "total": na, "rate": _rate(ua, na), "ci95_cluster_bootstrap": cluster_interval(records, "numbers_unverified_after", "numbers_total_after")},
        "turns_with_unverified_before": sum(1 for t in ok_turns if t["numbers_unverified_before"]),
        "turns_with_unverified_after": sum(1 for t in ok_turns if t["numbers_unverified_after"]),
        "turns_regenerated": sum(1 for t in ok_turns if t["regenerated"]),
        "regeneration_kept": sum(1 for t in ok_turns if t["regenerated"] and t["kept"] == "regenerated"),
        "turns_with_badge": sum(1 for t in ok_turns if t["badge"]),
    }
    tax = {"before_gate": {c: 0 for c in score.CLASSES}, "after_gate": {c: 0 for c in score.CLASSES}}
    for t in ok_turns:
        for f in t["findings_before"]: tax["before_gate"][f["class"]] += 1
        for f in t["findings_after"]: tax["after_gate"][f["class"]] += 1
    out["taxonomy"] = tax
    base = {d: {c: 0 for c in score.CLASSES} for d in ("3", "4")}
    for r in records:
        for d, cnt in (r.get("taxonomy_chance_baseline") or {}).items():
            for c, v in cnt.items(): base[d][c] += v
    out["taxonomy_chance_baseline"] = base
    bykind = {}
    for t in ok_turns:
        b = bykind.setdefault(t["kind"], {"turns": 0, "correct": 0, "found": 0, "must": 0, "unverified_before": 0, "total_before": 0,
                                          "unverified_after": 0, "total_after": 0})
        b["turns"] += 1; b["correct"] += t["score"]["correct"]; b["found"] += len(t["score"]["found"]); b["must"] += t["score"]["n_must"]
        b["unverified_before"] += t["numbers_unverified_before"]; b["total_before"] += t["numbers_total_before"]
        b["unverified_after"] += t["numbers_unverified_after"]; b["total_after"] += t["numbers_total_after"]
    for b in bykind.values(): b["correct_rate"] = _rate(b["correct"], b["turns"]); b["found_rate"] = _rate(b["found"], b["must"])
    out["by_question_type"] = {k: bykind[k] for k in scripts.KINDS if k in bykind}
    out["correctness"] = {"correct_turns": sum(t["score"]["correct"] for t in ok_turns), "turns": len(ok_turns),
                          "expected_numbers_found": sum(len(t["score"]["found"]) for t in ok_turns),
                          "expected_numbers": sum(t["score"]["n_must"] for t in ok_turns),
                          "forbidden_values_present": sum(len(t["score"]["forbidden"]) for t in ok_turns)}
    calls = [c for t in ok_turns for c in t["tool_calls"]]
    cnt = {s: sum(1 for c in calls if c["status"] == s) for s in ("valid", "invalid", "failed")}
    nca = [c for c in calls if c["name"] == "nca_run"]
    out["tool_calls"] = {**cnt, "total": len(calls), "validity_rate": _rate(cnt["valid"], len(calls)),
                         "nca_run_calls": len(nca), "nca_run_right_dose": sum(1 for c in nca if c.get("dose_ok")),
                         "nca_run_right_route": sum(1 for c in nca if c.get("route_ok")),
                         "memory_calls": _sum(ok_turns, "memory_calls"),
                         "by_tool": {n: sum(1 for c in calls if c["name"] == n) for n in sorted({c["name"] for c in calls})}}
    walls = [t["wall_s"] for t in ok_turns]
    out["time"] = {"mean_wall_s_per_turn": sum(walls) / len(walls) if walls else None,
                   "mean_prompt_tokens_first_call": (sum(t["prompt_tokens"] for t in ok_turns) / len(ok_turns)) if ok_turns else None,
                   "total_wall_s": sum(r["wall_s"] for r in records)}
    out["per_exercise"] = []
    for r in records:
        ts = [t for t in r["turns"] if "error" not in t]
        out["per_exercise"].append({
            "id": r["id"], "family": r["family"], "dose": f"{r['dose']['amount']} {r['dose']['unit']}", "units": f"{r['units']['time']}, {r['units']['conc']}",
            "turns": len(r["turns"]), "turns_failed": len(r["turns"]) - len(ts),
            "unverified_before": _sum(ts, "numbers_unverified_before"), "total_before": _sum(ts, "numbers_total_before"),
            "unverified_after": _sum(ts, "numbers_unverified_after"), "total_after": _sum(ts, "numbers_total_after"),
            "correct_turns": sum(t["score"]["correct"] for t in ts), "badge_turns": sum(1 for t in ts if t["badge"]),
            "calls_valid": sum(1 for t in ts for c in t["tool_calls"] if c["status"] == "valid"),
            "calls_total": sum(len(t["tool_calls"]) for t in ts),
            "mean_wall_s": (sum(t["wall_s"] for t in ts) / len(ts)) if ts else None})
    return out

def _pct(x): return "n/a" if x is None else f"{100 * x:.1f} %"
def _ci(c): return "" if not c else f" (95 % CI over exercises {100 * c[0]:.1f}-{100 * c[1]:.1f} %)"

def render_md(rep):
    h, c, t, tm = rep["hallucination"], rep["correctness"], rep["tool_calls"], rep["time"]
    L = ["# Apothicaire benchmark report", ""]
    m = rep.get("meta") or {}
    if m: L += [", ".join(f"{k}: {v}" for k, v in m.items()), ""]
    b, a = h["before_gate"], h["after_gate"]
    L += [f"**Hallucination rate = numbers not found in a tool result or user message / numbers checked (deterministic gate `gate.py`).**", "",
          f"- before the gate's regeneration (first drafts): **{b['unverified']} / {b['total']} = {_pct(b['rate'])}**{_ci(b['ci95_cluster_bootstrap'])}",
          f"- in the answers shown (gate in the loop): **{a['unverified']} / {a['total']} = {_pct(a['rate'])}**{_ci(a['ci95_cluster_bootstrap'])}",
          f"- {rep['exercises']} exercises, {rep['turns']} turns ({rep['turns_failed']} failed by an error); turns with an unverified number: "
          f"{h['turns_with_unverified_before']} before, {h['turns_with_unverified_after']} after; regenerated {h['turns_regenerated']} "
          f"(regeneration kept {h['regeneration_kept']}); turns shown with the badge: {h['turns_with_badge']}", "",
          "## Failure taxonomy (unverified numbers)", "", "| class | before the gate | in the answers shown |", "|---|---|---|"]
    for k in score.CLASSES: L.append(f"| {k} | {rep['taxonomy']['before_gate'][k]} | {rep['taxonomy']['after_gate'][k]} |")
    L += ["", "Classes are heuristics (`bench/score.py`); the unverified counts above never depend on them. Chance baseline: how the "
          "same rules classify random numbers of 3 and 4 significant digits drawn over each exercise's range of tool values "
          "(a class whose baseline share is large is weak evidence at that precision):", "",
          "| class | random 3-digit numbers | random 4-digit numbers |", "|---|---|---|"]
    b3, b4 = rep["taxonomy_chance_baseline"]["3"], rep["taxonomy_chance_baseline"]["4"]
    n3, n4 = sum(b3.values()) or 1, sum(b4.values()) or 1
    for k in score.CLASSES: L.append(f"| {k} | {_pct(b3[k] / n3)} | {_pct(b4[k] / n4)} |")
    L += ["",
          f"## Correctness: {c['correct_turns']} / {c['turns']} turns fully correct; expected numbers found {c['expected_numbers_found']} / {c['expected_numbers']}; "
          f"forbidden (converted or computed) values present in {c['forbidden_values_present']} answers", "",
          "| question type | turns | correct | found / expected numbers | unverified / total before | unverified / total shown |", "|---|---|---|---|---|---|"]
    for k, v in rep["by_question_type"].items():
        L.append(f"| {k} | {v['turns']} | {v['correct']} ({_pct(v['correct_rate'])}) | {v['found']} / {v['must']} | "
                 f"{v['unverified_before']} / {v['total_before']} | {v['unverified_after']} / {v['total_after']} |")
    L += ["", f"## Tool calls: {t['valid']} valid, {t['invalid']} invalid, {t['failed']} failed of {t['total']} (validity {_pct(t['validity_rate'])})", "",
          f"`nca_run` calls: {t['nca_run_calls']}, with the right dose {t['nca_run_right_dose']}, with the right route {t['nca_run_right_route']}; "
          f"memory calls (zoom / read_message): {t['memory_calls']}; by tool: {t['by_tool']}. "
          "invalid = unknown tool, invalid_parameters, unknown_worksheet / unknown_analysis or any rejection; failed = accepted but the analysis errs for every subject.", "",
          f"## Time: mean {tm['mean_wall_s_per_turn']:.1f} s per turn, mean {tm['mean_prompt_tokens_first_call']:.0f} prompt tokens (first call), total {tm['total_wall_s'] / 60:.0f} min" if tm["mean_wall_s_per_turn"] is not None else "## Time: n/a",
          "", "## Per exercise", "",
          "| exercise | dose | units | unverified / total before | unverified / total shown | correct turns | badge turns | calls valid / total | mean s per turn |",
          "|---|---|---|---|---|---|---|---|---|"]
    for e in rep["per_exercise"]:
        w = "n/a" if e["mean_wall_s"] is None else f"{e['mean_wall_s']:.1f}"
        L.append(f"| {e['id']} | {e['dose']} | {e['units']} | {e['unverified_before']} / {e['total_before']} | {e['unverified_after']} / {e['total_after']} | "
                 f"{e['correct_turns']} / {e['turns'] - e['turns_failed']} | {e['badge_turns']} | {e['calls_valid']} / {e['calls_total']} | {w} |")
    return "\n".join(L) + "\n"

def load_records(run_dir, ids):
    out = []
    for i in ids:
        p = os.path.join(run_dir, i + ".json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f: out.append(json.load(f))
    return out

def write_report(run_dir, records, meta):
    rep = build_report(records, meta)
    with open(os.path.join(run_dir, "report.json"), "w", encoding="utf-8") as f: json.dump(rep, f, ensure_ascii=False, indent=1)
    with open(os.path.join(run_dir, "report.md"), "w", encoding="utf-8") as f: f.write(render_md(rep))
    return rep

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--first", type=int, default=0, help="only the first N exercises (fixed order: sorted ids)")
    ap.add_argument("--ids", default="", help="comma-separated exercise ids")
    ap.add_argument("--resume", action="store_true", help="skip the exercises whose <id>.json exists")
    ap.add_argument("--report-only", action="store_true")
    a = ap.parse_args(); optchat._utf8_stdout()
    run_dir = os.path.join(RUNS, a.date); os.makedirs(run_dir, exist_ok=True)
    dirs = mk.list_exercises()
    if a.ids: dirs = [d for d in dirs if os.path.basename(d) in a.ids.split(",")]
    if a.first: dirs = dirs[:a.first]
    ids = [os.path.basename(d) for d in dirs]
    if not a.report_only:
        for d in dirs:
            i = os.path.basename(d)
            if a.resume and os.path.exists(os.path.join(run_dir, i + ".json")): print("skip", i); continue
            t0 = time.time(); r = run_exercise(d, run_dir)
            ok = [t for t in r["turns"] if "error" not in t]
            print(f"{i}: {len(ok)}/{len(r['turns'])} turns, unverified {sum(t['numbers_unverified_before'] for t in ok)}/"
                  f"{sum(t['numbers_total_before'] for t in ok)} before, {sum(t['numbers_unverified_after'] for t in ok)}/"
                  f"{sum(t['numbers_total_after'] for t in ok)} shown, {time.time() - t0:.0f} s", flush=True)
            write_report(run_dir, load_records(run_dir, ids), {"date": a.date, "exercises_run": len(ids), "model": "Bonsai 2 27B (Ternary-Bonsai-2-27B-PTQ1_0), temperature 0.3, no fixed seed"})
    rep = write_report(run_dir, load_records(run_dir, ids), {"date": a.date, "exercises_run": len(ids), "model": "Bonsai 2 27B (Ternary-Bonsai-2-27B-PTQ1_0), temperature 0.3, no fixed seed"})
    h = rep["hallucination"]
    print(f"hallucination: {h['before_gate']['unverified']}/{h['before_gate']['total']} before, {h['after_gate']['unverified']}/{h['after_gate']['total']} shown")
    print("report:", os.path.join(run_dir, "report.md"))

if __name__ == "__main__":
    main()
