#!/usr/bin/env python
"""Runs my out-of-distribution requests through the decision harness with MY gold decisions (the "gold path by hand").

  python decision/ood/run_ood_goldpath.py [--limit N]

For every line of requests.jsonl the harness gets its state by hand (the exercise CSV, the dose / route sentence, the
BLQ note, the analyses of prior_analyses: they are really created through Caladrius so the ids exist), then a decider
returns my gold labels for that line (the pair of a compare line is translated to the real analysis ids). The answer is
kept as is. This is the ceiling of the pipeline on my requests: it tests my gold and the templates, not the model.
Writes decision/ood/runs/goldpath.json and prints one line per request.
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DECISION = os.path.dirname(HERE)
AGENT = os.path.dirname(DECISION)
for p in (AGENT, DECISION):
    if p not in sys.path: sys.path.insert(0, p)
import harness  # noqa: E402
import make_dataset as md  # noqa: E402
from bench import make_exercises as mk, scripts  # noqa: E402

PARAMS = list(md.PARAMETERS)


def exercise_dir(ex):
    if ex.startswith("oodx"): return os.path.join(HERE, "exercises", ex)
    return os.path.join(AGENT, "bench", "exercises", ex)


def intro_of(meta, csv, line):
    if line["turn"] == 1: return line["request"]
    try:
        return md.split_first_message(scripts.build_script(meta, csv)[0]["question"])["intro"]
    except Exception:
        r = meta["route"]
        route_txt = ("per os" if r == "extravascular" else "en bolus intraveineux" if r == "iv_bolus" else
                     f"en perfusion intraveineuse de {r['iv_infusion']['duration']} {meta['units']['time']}")
        return f"{meta['dose']['amount']} {meta['dose']['unit']} {route_txt}"


def notes_of(meta, csv):
    if not meta.get("blq"): return []
    try:
        return md.split_first_message(scripts.build_script(meta, csv)[0]["question"])["notes"]
    except Exception:
        return [f"Les 0 correspondent à des valeurs sous la LLOQ ({meta['blq']['lloq']} {meta['units']['conc']})."]


def engine_route(meta, intro):
    r = meta["route"]
    if isinstance(r, dict): return {"iv_infusion": {"duration": r["iv_infusion"]["duration"]}}
    return harness.ENGINE_ROUTE.get(r, "extravascular")


def classify(ans):
    a = ans.strip()
    checks = [("Je n'ai pas encore de données", "T_NO_DATA"),
              ("Je ne lance pas l'analyse : la voie", "T_ASK_ROUTE"),
              ("Je ne lance pas l'analyse : la dose n'a pas d'unité", "T_ASK_DOSE_UNIT"),
              ("Je ne lance pas l'analyse : je ne trouve pas la dose", "T_ASK_DOSE"),
              ("Je ne lance pas l'analyse : la durée de la perfusion n'est pas indiquée", "T_ASK_DURATION"),
              ("Je ne lance pas l'analyse : la durée de la perfusion est donnée en", "T_ASK_DURATION_UNIT"),
              ("Aucune analyse n'est encore faite", "T_NO_ANALYSIS"),
              ("Cette demande (", "T_NOT_WIRED"),
              ("L'analyse non compartimentale est faite", "T_NO_PARAMETER"),
              ("Quelles analyses faut-il comparer", "T_WHICH_PAIR"),
              ("Je n'ai pas pu interpréter", "T_UNDECIDED"),
              ("Comparaison calculée par Caladrius", "rendered_compare"),
              ("Résultats de Caladrius", "rendered_params"),
              ("Réglages de l'analyse", "rendered_recall")]
    for prefix, name in checks:
        if a.startswith(prefix): return name
    if "n'est pas calculé par Caladrius" in a: return "T_NOT_AVAILABLE"
    return "other"


def expected_outcome(line):
    g = line["gold"]
    if g["is_not_available"]: return "refusal"
    if g["analysis"] in ("fit_pk1", "fit_pk2", "simulate"): return "T_NOT_WIRED"
    if g["analysis"] == "compare":
        return "rendered_compare" if g["compare_pair"] != "not_applicable" else "which_or_no_analysis"
    if g["analysis"] == "none_needed":
        return "rendered_recall" if not g["asked"] else "rendered_params"
    # nca: missing dose unit / dose / route / duration produce a question
    if not g["dose_has_unit"]: return "T_ASK_DOSE_UNIT"
    if g["route"] == "unknown": return "T_ASK_ROUTE"
    return "rendered_params"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=0); a = ap.parse_args()
    lines = [json.loads(x) for x in open(os.path.join(HERE, "requests.jsonl"), encoding="utf-8") if x.strip()]
    if a.limit: lines = lines[:a.limit]
    out_rows = []
    for i, line in enumerate(lines):
        meta, csv = mk.load(exercise_dir(line["exercise"]))
        intro, notes = intro_of(meta, csv, line), notes_of(meta, csv)
        gold = line["gold"]
        id_map = {}
        holder = {}

        def decide(state, questions, line=line, gold=gold, id_map=id_map):
            pair = gold["compare_pair"]
            if "+" in pair:
                x, y = pair.split("+")
                pair = f"{id_map.get(x, x)}+{id_map.get(y, y)}"
            ans = {"analysis": gold["analysis"], "route": gold["route"], "auc_method": gold["auc_method"],
                   "dose_has_unit": "true" if gold["dose_has_unit"] else "false",
                   "is_not_available": "true" if gold["is_not_available"] else "false", "compare_pair": pair}
            for k in PARAMS: ans[f"asked_{k}"] = "true" if k in gold["asked"] else "false"
            holder["calls"] = holder.get("calls", 0) + 1
            return ans

        h = harness.Harness(decide)
        h.data = {"intro": intro, "csv": csv, "notes": notes}
        h.units = {}
        setup = []
        try:
            if line["prior_analyses"]:
                h._import()
                dose, _ = harness.parse_dose(intro)
                route = engine_route(meta, intro)
                for pa in line["prior_analyses"]:
                    d = h._run_nca(dose, route, pa["auc_method"])
                    setup.append({"wanted": pa["id"], "engine_id": (d or {}).get("analysis"), "method": pa["auc_method"], "ok": d is not None})
                    if d is not None: id_map[str(pa["id"])] = d.get("analysis")
            ans, info = h.turn(line["request"])
            got = classify(ans)
            exp = expected_outcome(line)
            row = {"id": line["id"], "exercise": line["exercise"], "turn": line["turn"], "tags": line["tags"],
                   "gold": gold, "intro": intro, "setup": setup, "outcome": got, "expected": exp,
                   "decide_calls": holder.get("calls", 0), "harness_notes": info["notes"],
                   "tool_errors": [{"name": c["name"], "ok": c["ok"], "error": c["text"][:160]} for c in h.tool_log if not c["ok"]],
                   "answer": ans}
            out_rows.append(row)
            print(f"{line['id']:8s} {got:22s} exp {exp:22s} calls {holder.get('calls', 0)}  {ans.splitlines()[0][:90]}")
        except Exception as e:
            out_rows.append({"id": line["id"], "error": f"{type(e).__name__}: {e}"})
            print(f"{line['id']:8s} CRASH {type(e).__name__}: {e}")
        finally:
            h.close()
    out = os.path.join(HERE, "runs"); os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "goldpath.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"lines": out_rows}, f, ensure_ascii=False, indent=1)
    ok = sum(1 for r in out_rows if r.get("outcome") == r.get("expected"))
    flexible = sum(1 for r in out_rows if r.get("outcome") == r.get("expected") or
                   (r.get("expected") == "which_or_no_analysis" and r.get("outcome") in ("T_WHICH_PAIR", "T_NO_ANALYSIS")))
    print(f"\n{ok}/{len(out_rows)} lines take the branch my gold asks for; {flexible} with the compare-pair pair of branches allowed")


if __name__ == "__main__":
    main()
