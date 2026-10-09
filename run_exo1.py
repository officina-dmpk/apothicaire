#!/usr/bin/env python
"""Scripted 4-turn French demo of Apothicaire v0 on exercise 1 (10 mg oral, one subject).

The CSV is private coursework: it is read at run time and only written to the transcript and the
chat memory of the run, both under agent/runs/. Usage: python run_exo1.py [csv path]
"""
import datetime, json, os, shutil, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
DATE = datetime.date.today().isoformat()
RUN_DIR = os.path.join(HERE, "runs")
DATA = os.path.join(RUN_DIR, f"{DATE}-exo1-data")
os.environ["APOTHICAIRE_DATA"] = DATA
sys.path.insert(0, HERE)
import apothicaire, gate, optchat  # noqa: E402

CSV_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    HERE, "..", "caladrius", "private", "coursework", "td1_exercice1_oral.csv")

def prompts(csv_text):
    return [
        "Voici les données de l'exercice 1 (10 mg par voie orale ; temps en h, concentration en ng/mL) :\n"
        f"{csv_text.strip()}\n"
        "Fais l'analyse non compartimentale avec la méthode linéaire des trapèzes et donne-moi Cmax, Tmax, "
        "AUC(0-tlast), AUC(0-inf), λz, t½, CL/F, Vz/F et MRT, avec les unités.",
        "Refais-la avec la méthode linear-up/log-down et compare les AUC.",
        "Le pourcentage extrapolé est-il acceptable ? Combien de points ont servi pour λz ?",
        "Rappelle-moi la dose et la méthode utilisée au premier tour.",
    ]

# ---------------------------------------------------------------- run
def main():
    optchat._utf8_stdout()
    with open(CSV_PATH, encoding="utf-8") as f: csv_text = f.read()
    if os.path.exists(DATA): shutil.rmtree(DATA)
    os.makedirs(RUN_DIR, exist_ok=True)
    ag = apothicaire.Apothicaire()
    prefix = apothicaire.static_prefix_tokens(ag)
    turns = []
    try:
        for k, q in enumerate(prompts(csv_text)):
            n_log = len(ag.tool_log); n_msgs = len(ag.store.log)
            t0 = time.time(); ans, st = ag.turn(q, verbose=True); wall = time.time() - t0
            calls = ag.tool_log[n_log:]
            msgs = ag.store.log[n_msgs:]
            mem_calls = [c for m in msgs if m["role"] == "tool_call" for c in optchat._calls_of(m)
                         if c["name"] in ("zoom", "read_message")]
            g = st.get("gate") or {}
            turns.append({"q": q, "answer": ans, "stat": st, "wall": round(wall, 1), "calls": calls,
                          "mem_calls": mem_calls, "gate": g})
            b4, af = g.get("before", {}), g.get("after", {})
            print(f"\n=== turn {k+1}: {round(wall,1)} s, prompt {st['prompt_tokens']} tok, "
                  f"{len(calls)} MCP call(s), {len(mem_calls)} memory call(s); unverified numbers "
                  f"{b4.get('numbers_unverified')}/{b4.get('numbers_total')} before the gate's regeneration, "
                  f"{af.get('numbers_unverified')}/{af.get('numbers_total')} in the answer shown\n{ans}")
            ag.wait_bg()        # let the compaction finish so it is not counted in the next turn
    finally:
        ag.close()
    write_transcript(turns, prefix, csv_text)

def totals(turns, key):
    unv = sum((t["gate"].get(key) or {}).get("numbers_unverified", 0) for t in turns)
    tot = sum((t["gate"].get(key) or {}).get("numbers_total", 0) for t in turns)
    return unv, tot

def write_transcript(turns, prefix, csv_text):
    u0, n0 = totals(turns, "before"); u1, n1 = totals(turns, "after")
    L = [f"# Apothicaire v0, exercice 1 ({DATE})", "",
         f"**Hallucinated numbers: {u1}/{n1} in the answers shown ({u0}/{n0} before the gate's regeneration).** "
         "Metric: numbers_unverified / numbers_total, from the deterministic gate (`gate.py`): a number of an answer "
         "is unverified when no number of a tool result or of a user message equals it once rounded to the digits "
         "written (unit conversions and values computed by the model count). numbers_total excludes the exempt "
         "numbers (small counts, years, steps; see `gate.py`).", "",
         f"Model: Bonsai 2 27B (llama.cpp PrismML, slot 0, 12k context). Memory: OptChat in `runs/{DATE}-exo1-data/`. "
         f"Tools: zoom, read_message + Caladrius MCP {', '.join(apothicaire.EXPOSED)}.",
         f"Static prefix (system prompt + 6 tool definitions + one word): **{prefix} tokens**.", "",
         "| turn | wall s | LLM rounds | prompt tok (1st call) | uncached tok | MCP calls (ok) | memory calls | "
         "unverified/total before regeneration | regenerated | unverified/total shown |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for k, t in enumerate(turns):
        s = t["stat"]; c = t["calls"]; g = t["gate"]; b4 = g.get("before", {}); af = g.get("after", {})
        L.append(f"| {k+1} | {t['wall']} | {s['rounds']} | {s['prompt_tokens']} | {s['uncached_tokens']} | "
                 f"{len(c)} ({sum(1 for x in c if x['ok'])}) | {len(t['mem_calls'])} | "
                 f"{b4.get('numbers_unverified')}/{b4.get('numbers_total')} | "
                 f"{'yes, kept ' + g['kept'] if g.get('regenerated') else 'no'} | "
                 f"{af.get('numbers_unverified')}/{af.get('numbers_total')} |")
    L.append(f"| **total** | | | | | | | **{u0}/{n0}** | | **{u1}/{n1}** |")
    for k, t in enumerate(turns):
        L += ["", f"## Tour {k+1}", "", "**Utilisateur :**", "", "```text", t["q"], "```", ""]
        for c in t["calls"]:
            args = dict(c["args"])
            if "csv" in args:
                same = [x.strip() for x in args["csv"].strip().splitlines()] == [x.strip() for x in csv_text.strip().splitlines()]
                args["csv"] = f"<{len(c['args']['csv'])} chars, {'identical to' if same else 'DIFFERENT from'} the CSV file>"
            L.append(f"- tool `{c['name']}` {'ok' if c['ok'] else 'ERROR'} — args `{json.dumps(args, ensure_ascii=False)}`")
            shown = c["shown"] if c["ok"] else c["text"]
            L += ["", "  <details><summary>result shown to the model</summary>", "", "  ```json",
                  "  " + shown[:4000], "  ```", "  </details>", ""]
        for c in t["mem_calls"]:
            L.append(f"- memory `{c['name']}` `{c['args']}`")
        s = t["stat"]; g = t["gate"]
        if g.get("regenerated"):
            L += ["", f"First draft (before the gate's regeneration; {len(g.get('first_findings', []))} unverified number(s)):", "",
                  "```text", g.get("first_answer", ""), "```"]
        L += ["", f"**Apothicaire** ({t['wall']} s, {s['rounds']} LLM round(s), prompt {s['prompt_tokens']} tokens, "
              f"{s['gen_tps']} tok/s) :", "", t["answer"], ""]
        fl = g.get("findings") or []
        first = g.get("first_findings") or fl
        L.append("Gate findings in the first draft: " + (", ".join(
            f"`{f['text']}` (nearest `{f['nearest_allowed']}`{', ' + f['hint'] if f.get('hint') else ''})" for f in first) or "none"))
        if g.get("regenerated"):
            L.append("Gate findings left in the answer shown: " + (", ".join(f"`{f['text']}`" for f in fl) or "none"))
    out = os.path.join(RUN_DIR, f"{DATE}-exo1.md")
    with open(out, "w", encoding="utf-8") as f: f.write("\n".join(L) + "\n")
    with open(os.path.join(RUN_DIR, f"{DATE}-exo1.json"), "w", encoding="utf-8") as f:
        json.dump({"prefix_tokens": prefix, "numbers_unverified_before": u0, "numbers_total_before": n0,
                   "numbers_unverified_shown": u1, "numbers_total_shown": n1, "turns": turns},
                  f, ensure_ascii=False, indent=1)
    print(f"numbers_unverified/numbers_total: {u0}/{n0} before regeneration, {u1}/{n1} shown")
    print("transcript:", out)

if __name__ == "__main__":
    main()
