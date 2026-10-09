#!/usr/bin/env python
"""Scores the trained decider of decision/decider_unsloth.py on the out-of-distribution requests (Part 2).

  .venv-unsloth/Scripts/python decision/ood/eval_ood_model.py [--limit N] [--model PATH]

For every line of decision/ood/requests.jsonl it rebuilds the state the harness would build at that turn
(decision/make_dataset.make_state with the exercise CSV, the dose / route sentence, the BLQ note and the analyses of
prior_analyses), asks the model the 20 closed questions of make_dataset.questions_for, and compares its labels with
the gold I wrote blind. Two scores are reported: against my gold, and against a variant where `auc_method` is replaced
by the project's stated convention (not_applicable unless the turn is the first NCA or a compare) because 16 of my 74
lines read `linear` on a result-reading turn where the dataset's convention is `not_applicable`.

Writes decision/ood/runs/eval_ood_model.json (per line and per question) and prints the tables.
"""
import argparse, collections, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DECISION = os.path.dirname(HERE)
AGENT = os.path.dirname(DECISION)
for p in (AGENT, DECISION):
    if p not in sys.path: sys.path.insert(0, p)
import make_dataset as md  # noqa: E402
from bench import make_exercises as mk, scripts  # noqa: E402

PARAMS = list(md.PARAMETERS)
QUESTIONS = [q for q in md.questions_for([2, 3]) if not q.startswith("asked_")] + [f"asked_{k}" for k in PARAMS]


def exercise_dir(ex):
    if ex.startswith("oodx"): return os.path.join(HERE, "exercises", ex)
    return os.path.join(AGENT, "bench", "exercises", ex)


def intro_of(meta, csv, line):
    """The dose / route / units sentence of the conversation. Turn 1: the request itself (it carries the dose, and the
    harness reads the dose from the first line of the first message). Later turns: the exercise's scripted dose sentence
    (the state's user_dose_sentence is the one from turn 1), or a sentence rebuilt from meta.json for my invented exercises."""
    if line["turn"] == 1: return line["request"]
    try:
        return md.split_first_message(scripts.build_script(meta, csv)[0]["question"])["intro"]
    except Exception:
        r = meta["route"]
        route_txt = ("per os" if r == "extravascular" else
                     "en bolus intraveineux" if r == "iv_bolus" else
                     f"en perfusion intraveineuse de {r['iv_infusion']['duration']} {meta['units']['time']}")
        return f"{meta['dose']['amount']} {meta['dose']['unit']} {route_txt}"


def notes_of(meta, csv):
    if not meta.get("blq"): return []
    try:
        return md.split_first_message(scripts.build_script(meta, csv)[0]["question"])["notes"]
    except Exception:
        return [f"Les 0 correspondent à des valeurs sous la LLOQ ({meta['blq']['lloq']} {meta['units']['conc']})."]


def build_state(line):
    meta, csv = mk.load(exercise_dir(line["exercise"]))
    analyses = [{"id": pa["id"], "kind": "nca", "auc_method": pa["auc_method"]} for pa in line["prior_analyses"]]
    state = md.make_state(csv, intro_of(meta, csv, line), notes_of(meta, csv), line["request"], analyses)
    questions = md.questions_for(sorted(a["id"] for a in analyses))
    return state, questions


def gold_answers(line):
    g = line["gold"]
    out = {"analysis": g["analysis"], "route": g["route"], "auc_method": g["auc_method"],
           "dose_has_unit": "true" if g["dose_has_unit"] else "false",
           "is_not_available": "true" if g["is_not_available"] else "false",
           "compare_pair": g["compare_pair"]}
    for k in PARAMS: out[f"asked_{k}"] = "true" if k in g["asked"] else "false"
    return out


def project_auc(line, answers):
    a = answers["analysis"]
    return "linear" if (a == "nca" and not line["prior_analyses"]) else ("lin_up_log_down" if a == "compare" else "not_applicable")


def score(rows, keys):
    per = collections.defaultdict(lambda: [0, 0]); exact = 0
    for r in rows:
        bad = 0
        for q in keys:
            per[q][1] += 1
            ok = r["pred"].get(q) == r["gold_a"].get(q)
            per[q][0] += ok
            bad += not ok
        exact += bad == 0
    return {q: tuple(v) for q, v in per.items()}, (exact, len(rows))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--model", default=None)
    a = ap.parse_args()
    if a.model: os.environ["D01_MODEL"] = a.model
    import decider_unsloth
    lines = [json.loads(x) for x in open(os.path.join(HERE, "requests.jsonl"), encoding="utf-8") if x.strip()]
    if a.limit: lines = lines[:a.limit]
    rows = []
    for i, line in enumerate(lines):
        state, questions = build_state(line)
        labels = decider_unsloth.decide(state, questions)
        info = decider_unsloth.decide.last_info
        gold_a = gold_answers(line)
        gold_proj = dict(gold_a); gold_proj["auc_method"] = project_auc(line, gold_a)
        pred = {q: (("true" if labels[q] else "false") if isinstance(labels[q], bool) else str(labels[q])) for q in labels}
        rows.append({"id": line["id"], "exercise": line["exercise"], "turn": line["turn"], "tags": line["tags"],
                     "request": line["request"], "pred": pred, "gold_a": gold_a, "gold_project": gold_proj,
                     "info": info.get("answers") if info else None})
        print(f"  {i + 1}/{len(lines)} {line['id']} {len(info['answers']) if info else 0} q", file=sys.stderr)
    keys = list(QUESTIONS)
    per, exact = score(rows, keys)
    # the project-convention variant
    for r in rows: r["_gold_a"] = r["gold_a"]; r["gold_a"] = r["gold_project"]
    perp, exactp = score(rows, keys)
    for r in rows: r["gold_a"] = r["_gold_a"]; del r["_gold_a"]
    # per tag
    tag_acc = {}
    for tag in sorted({t for r in rows for t in r["tags"]}):
        sub = [r for r in rows if tag in r["tags"]]
        ks = [q for q in keys]
        pa, ex = score(sub, ks)
        tag_acc[tag] = {"lines": len(sub), "questions_right": sum(v[0] for v in pa.values()), "questions": sum(v[1] for v in pa.values()),
                        "exact_lines": ex[0]}
    rep = {"model": os.environ.get("D01_MODEL", "default"), "lines": len(rows), "questions_per_line": len(keys),
           "per_question": {q: {"right": per[q][0], "total": per[q][1]} for q in keys},
           "exact_lines": exact[0], "questions_right": sum(v[0] for v in per.values()), "questions": sum(v[1] for v in per.values()),
           "per_question_project_convention": {q: {"right": perp[q][0], "total": perp[q][1]} for q in keys},
           "exact_lines_project_convention": exactp[0],
           "questions_right_project_convention": sum(v[0] for v in perp.values()),
           "per_tag": tag_acc, "rows": rows}
    out = os.path.join(HERE, "runs"); os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "eval_ood_model.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != "rows"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
