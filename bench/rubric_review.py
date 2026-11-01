#!/usr/bin/env python
"""Review of a change of the rubric on the stored runs (FROZEN_SET.md §6.2, §7, T-066). No model and no engine; the stored runs are
read and never written. Each run is scored against the gold it ran with (`git show <commit>:bench/exercises/...`), not the gold of
today: T-111 moved the gold by a few ulps, and an answer that quotes a raw 16-digit value no longer matches the moved value.

  python bench/rubric_review.py rescore [--before main]   the figures as published next to the rescored ones, per configuration
                                                          (writes bench/runs/RUBRIC-RESCORE-<version>.md)
  python bench/rubric_review.py sample                    the seeded draw of §7 for the human labelling, without any verdict
                                                          (writes bench/labelling/SHEET.md, sample.json, labels.csv)
  python bench/rubric_review.py agreement                 the labels of bench/labelling/labels.csv against the rubric

`--before` names the commit whose `score.py` gave the figures as published: `rescore` runs it too and checks that it gives back every
stored outcome, so that a moved turn is the change of the scorer and nothing else.
"""
import argparse, collections, csv, importlib.util, json, os, random, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
if AGENT not in sys.path: sys.path.insert(0, AGENT)
from bench import mutations, run_bench as rb, score, scripts, stats  # noqa: E402

GOLD_BEFORE_UNITS, GOLD_BEFORE_T111 = "e5a010d^", "76af559^"
RUNS = rb.RUNS
# (name, folder under bench/runs, whether it holds seed-<s> folders, gold the run was scored with)
CONFIGS = (("2026-10-09", "2026-10-09", False, GOLD_BEFORE_UNITS), ("2026-10-09b", "2026-10-09b", False, GOLD_BEFORE_UNITS),
           ("2026-10-17-27b-upstream-full", "2026-10-17-27b-upstream-full", False, GOLD_BEFORE_UNITS),
           ("2026-10-17-gate-v2", "2026-10-17-gate-v2", False, GOLD_BEFORE_UNITS), ("2026-10-18-gate-v2b", "2026-10-18-gate-v2b", False, GOLD_BEFORE_UNITS),
           ("v1 (demo gate)", "decision/v1", True, GOLD_BEFORE_T111), ("v2", "decision/v2", True, GOLD_BEFORE_T111),
           ("nolm", "nolm-dev-2026-10-21/nolm", True, GOLD_BEFORE_T111),
           ("Sonnet 5.5", "frontier-dev-2026-10-22/v1+claude-sonnet-5-5", True, GOLD_BEFORE_T111),
           ("Opus 5.5", "frontier-dev-2026-10-22/v1+claude-opus-5-5", True, GOLD_BEFORE_T111),
           ("Sonnet 5.5 + scope", "frontier-dev-2026-10-22/v1+claude-sonnet-5-5+scope", True, GOLD_BEFORE_T111),
           ("27B + scope", "frontier-dev-2026-10-22-27b-scope/v1+scope", True, GOLD_BEFORE_T111),
           ("v3 (grammar arm)", "grammar-dev/v3", True, GOLD_BEFORE_T111))
# the comparisons the ledger reads (name of the first, name of the second)
PAIRS = (("v1 (demo gate)", "v2"), ("27B + scope", "Sonnet 5.5 + scope"), ("v1 (demo gate)", "Sonnet 5.5 + scope"), ("v1 (demo gate)", "27B + scope"))

LABELLING = os.path.join(HERE, "labelling")
SAMPLE_SEED = 20261101          # fixed before the draw; the draw is never repeated with another seed (§7)
SAMPLE_PER_KIND = 5
LABELS = ("CORRECT", "WRONG")

# ---------------------------------------------------------------- stored runs
def _git(*args):
    return subprocess.run(["git", *args], cwd=AGENT, capture_output=True, check=True).stdout.decode("utf-8")

_gold = {}
def gold(commit, ex):
    """(meta, CSV text, script) of an exercise at a commit."""
    if (commit, ex) not in _gold:
        meta = json.loads(_git("show", f"{commit}:bench/exercises/{ex}/meta.json"))
        text = _git("show", f"{commit}:bench/exercises/{ex}/data.csv")
        _gold[commit, ex] = (meta, text, scripts.build_script(meta, text))
    return _gold[commit, ex]

def records(folder, seeded):
    """[(seed or None, record)] of a configuration, in a fixed order."""
    root = os.path.join(RUNS, folder)
    dirs = [(int(d[5:]), os.path.join(root, d)) for d in sorted(os.listdir(root)) if d.startswith("seed-")] if seeded else [(None, root)]
    out = []
    for seed, d in dirs:
        for fn in sorted(os.listdir(d)):
            if fn.startswith("ex") and fn.endswith(".json"):
                with open(os.path.join(d, fn), encoding="utf-8") as f: out.append((seed, json.load(f)))
    return out

def judge(mod, rec, st, meta, text, prior):
    """(outcome, rubric) of a stored turn under a version of score.py; the stored record is not touched."""
    if "error" in rec: return "ERROR", None
    _, usage = rb.resolve_turn(meta, st, prior, rec.get("tool_calls", []))
    r = mod.rubric_turn(rec.get("answer") or "", st, meta, [c.get("shown", "") for c in rec.get("tool_calls", [])], usage, rb.BADGE_MARK,
                        scripts.csv_numbers(text))
    return mod.outcome_of(rec, r), r

def score_at(commit):
    """The module `bench/score.py` of a commit."""
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "score_before.py")
        with open(p, "w", encoding="utf-8", newline="\n") as f: f.write(_git("show", f"{commit}:bench/score.py"))
        spec = importlib.util.spec_from_file_location("score_before", p)
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

# ---------------------------------------------------------------- rescore
def rescore_config(name, folder, seeded, commit, before):
    """The figures of one configuration under the two scorers, and the turns that move."""
    c = {"name": name, "turns": 0, "dev": 0, "before": 0, "after": 0, "stored": 0, "stored_same": 0, "moved": [], "by_kind": {},
         "pass_before": collections.defaultdict(list), "pass_after": collections.defaultdict(list), "gold": commit}
    for seed, r in records(folder, seeded):
        meta, text, script = gold(commit, r["id"])
        ok_b = ok_a = True
        for k, (t, st) in enumerate(zip(r["turns"], script)):
            ob, rb_ = judge(before, t, st, meta, text, r["turns"][:k])
            oa, ra = judge(score, t, st, meta, text, r["turns"][:k])
            c["turns"] += 1; c["dev"] += bool(t.get("score", {}).get("correct")) and "error" not in t
            c["before"] += ob == "CORRECT"; c["after"] += oa == "CORRECT"; ok_b &= ob == "CORRECT"; ok_a &= oa == "CORRECT"
            if "outcome" in t: c["stored"] += 1; c["stored_same"] += t["outcome"] == ob
            b = c["by_kind"].setdefault(t["kind"], [0, 0, 0]); b[0] += 1; b[1] += ob == "CORRECT"; b[2] += oa == "CORRECT"
            if ob != oa:
                c["moved"].append({"seed": seed, "id": r["id"], "turn": t["turn"], "kind": t["kind"], "before": ob, "after": oa,
                                   "reasons": (rb_ or {}).get("reasons", []), "left": (ra or {}).get("reasons", [])})
        c["pass_before"][r["id"]].append(ok_b); c["pass_after"][r["id"]].append(ok_a)
    return c

def _passed(per): return sorted(i for i, v in per.items() if all(v))
def _pass1(per): return sum(sum(v) / len(v) for v in per.values()) / len(per) if per else 0.0

def render(configs, before_commit):
    L = [f"# Stored runs rescored with the rubric {score.RUBRIC_VERSION}", "",
         f"Generated by `python bench/rubric_review.py rescore --before {before_commit}`. No model and no engine: the stored answers and tool "
         "calls, each run against the gold it ran with. **The stored records and reports are not modified, and the figures on the left stay the "
         "published ones**: the ledger, the §8 decision and the readings of `FRONTIER_ARM.md` and `GRAMMAR_ARM.md` were made on them. All of "
         "this is in-sample development data.", "",
         "The change (FROZEN_SET.md §6.2, implementation note of 2026-11-01): false negatives read in the failed turns: a threshold of another "
         "quantity taken as a verdict, French names of the method, a value before the method in parentheses, a label in a method heading, a count "
         "in words, a difference under a heading. It makes the rubric accept more: the mutation suite was extended with the same layouts in both "
         "directions.", "",
         "Columns: the development scorer as published; CORRECT under the rubric as published; CORRECT under this rubric; exercises passed "
         "(all turns CORRECT on every seed) before and after; the mean pass rate over seeds (pass^1) before and after.", "",
         "| configuration | turns | correct, development scorer | CORRECT, published | CORRECT, now | exercises passed, published | exercises passed, now | pass^1, published | pass^1, now |",
         "|---|---|---|---|---|---|---|---|---|"]
    for c in configs:
        L.append(f"| {c['name']} | {c['turns']} | {c['dev']} | {c['before']} | {c['after']} | {len(_passed(c['pass_before']))} / {len(c['pass_before'])} | "
                 f"{len(_passed(c['pass_after']))} / {len(c['pass_after'])} | {100 * _pass1(c['pass_before']):.1f} % | {100 * _pass1(c['pass_after']):.1f} % |")
    stored, same = sum(c["stored"] for c in configs), sum(c["stored_same"] for c in configs)
    L += ["", f"Check: the scorer of `{before_commit}`, on the gold of each run, gives back {same} of the {stored} outcomes stored in the records. The five "
          "runs of October 9 to 18 store no outcome; their column is `bench/runs/RUBRIC-RESCORE.md`.", "",
          "## Comparisons the ledger reads", "",
          "Exact McNemar on the exercises passed on every seed, as in `run_frozen.paired_section`. **The readings written in the ledger are not "
          "reread here**: they stand on the published figures unless Abdou decides otherwise.", "",
          "| pair | published: both, only first, only second, p | now: both, only first, only second, p |", "|---|---|---|"]
    by = {c["name"]: c for c in configs}
    def pair(a, b, key):
        pa, pb = set(_passed(by[a][key])), set(_passed(by[b][key]))
        x, y = pa - pb, pb - pa
        return f"{len(pa & pb)}, {len(x)}, {len(y)}, p = {stats.mcnemar_exact(len(x), len(y)):.3g}"
    for a, b in PAIRS: L.append(f"| {a} / {b} | {pair(a, b, 'pass_before')} | {pair(a, b, 'pass_after')} |")
    for c in configs:
        L += ["", f"## {c['name']}", "", f"Gold: `{c['gold']}`. Turns that move: {len(c['moved'])}.", ""]
        L += ["| question type | turns | CORRECT, published | CORRECT, now |", "|---|---|---|---|"]
        L += [f"| {k} | {v[0]} | {v[1]} | {v[2]} |" for k, v in sorted(c["by_kind"].items(), key=lambda kv: scripts.KINDS.index(kv[0])) if v[1] != v[2]]
        if c["moved"]:
            L += ["", "| seed | exercise | turn | published | now | why it failed | what still fails |", "|---|---|---|---|---|---|---|"]
            L += [f"| {m['seed'] or ''} | {m['id']} | {m['turn']} {m['kind']} | {m['before']} | {m['after']} | {'; '.join(m['reasons']) or '(none)'} | "
                  f"{'; '.join(m['left']) or '(none)'} |" for m in c["moved"]]
    return "\n".join(L) + "\n"

def cmd_rescore(before_commit):
    before = score_at(before_commit)
    configs = [rescore_config(n, f, s, g, before) for n, f, s, g in CONFIGS]
    out = os.path.join(RUNS, f"RUBRIC-RESCORE-{score.RUBRIC_VERSION}.md")
    with open(out, "w", encoding="utf-8", newline="\n") as f: f.write(render(configs, before_commit))
    print("written", out)
    for c in configs: print(f"{c['name']}: {c['before']} -> {c['after']} / {c['turns']}; exercises {len(_passed(c['pass_before']))} -> {len(_passed(c['pass_after']))}; "
                            f"stored outcomes given back {c['stored_same']} / {c['stored']}")

# ---------------------------------------------------------------- the labelling of §7
_LABELLED = tuple(c for c in CONFIGS if c[2])          # the runs of 3 seeds, made on the gold with units for the rubric

def draw():
    """The seeded draw of §7: SAMPLE_PER_KIND turns of each of the 8 turn kinds, among every turn of the development runs that has an
    answer. The draw reads no verdict. The shuffled order gives the sheet its numbers, so a number says nothing of the kind or the run."""
    pool = {k: [] for k in scripts.KINDS}
    for name, folder, seeded, commit in _LABELLED:
        for seed, r in records(folder, seeded):
            for t in r["turns"]:
                if "error" not in t and (t.get("answer") or "").strip():
                    pool[t["kind"]].append({"config": name, "folder": folder, "seed": seed, "exercise": r["id"], "turn": t["turn"], "gold": commit})
    rng = random.Random(SAMPLE_SEED)
    picks = [x for k in scripts.KINDS for x in rng.sample(pool[k], SAMPLE_PER_KIND)]
    rng.shuffle(picks)
    return [dict(p, id=f"S{i:02d}") for i, p in enumerate(picks, 1)], {k: len(v) for k, v in pool.items()}

def _stored_turn(p):
    path = os.path.join(RUNS, p["folder"], f"seed-{p['seed']}", p["exercise"] + ".json")
    with open(path, encoding="utf-8") as f: r = json.load(f)
    return r, r["turns"][p["turn"] - 1]

def _expected(p):
    """What the answer must state, from the gold alone: the Markdown lines of one sheet entry. No verdict of the scorer."""
    r, t = _stored_turn(p)
    meta, text, script = gold(p["gold"], p["exercise"])
    st = script[p["turn"] - 1]; kind = st["kind"]
    _, usage = rb.resolve_turn(meta, st, r["turns"][:p["turn"] - 1], t.get("tool_calls", []))
    items, alts = score.rubric_items(st, meta, usage)
    num = mutations.num
    L = [f"- {it['label']}{' (facultatif, mais juste si donné)' if it.get('optional') else ''} : {num(it['value'])} {it.get('unit') or ''}".rstrip() for it in items]
    for alt in alts:
        L.append("- " + " ou ".join(f"{a['label']} : {num(a['value'])} {a.get('unit') or ''}".rstrip() for a in alt) + " (signe ou valeur absolue)")
    e = st["expect"]
    if kind == "half_life":
        pext = scripts.truth_value(meta, "aucpext.obs")
        L.append(f"- verdict attendu : {'acceptable' if pext <= score.VERDICT_THRESHOLD else 'non acceptable'} ({pext:.3g} % extrapolés)")
    if kind == "recall": L += [f"- voie : {scripts.route_fr(meta)}", "- méthode d'AUC : linéaire (trapèzes)"]
    if kind == "not_available": L.append(f"- dire que {e.get('not_calculated_parameter')} n'est pas calculé, sans aucune valeur étiquetée avec lui")
    allowed = ()                                                      # rubric_turn: asked for in the compare turn, or the engine's own
    if kind == "compare": allowed = ("AUC difference", "AUC ratio", "AUC difference in % of the linear AUC", "AUC difference in % of the log-down AUC") \
        if (usage or {}).get("usable") else ("AUC difference", "AUC difference in % of the linear AUC")
    banned = [i for i in e.get("must_not", []) if i["label"].strip() not in allowed]
    if banned: L.append("- valeurs interdites (converties ou calculées par le modèle, sauf copie exacte d'un résultat d'outil) : "
                        + ", ".join(f"{i['label'].strip()} = {num(i['value'])}" for i in banned))
    return st["question"], kind, L, t.get("answer", "").split(rb.BADGE_MARK)[0]

SHEET_HEAD = """# Étiquetage humain de 40 tours (FROZEN_SET.md §7)

Tirage aléatoire de {n} tours des runs de développement : {per} par type de tour, graine {seed}, fixée avant le tirage. Les numéros ne disent ni
le run, ni le modèle, ni le type de tour. **Cette feuille ne contient aucun verdict du scorer**, et `sample.json` non plus ; `sample.json` dit
de quel run vient chaque tour, donc ne l'ouvre pas avant d'avoir fini, et ne lance pas `rubric_review.py agreement` avant d'avoir tout étiqueté.

Pour chaque tour, écris `CORRECT` ou `WRONG` dans `labels.csv` (colonne `label`), avec un mot dans `note` si le cas te fait hésiter.
L'accord sera calculé avant toute résolution, puis chaque désaccord sera résolu avant le gel, en corrigeant le scorer ou en écrivant le cas
dans la rubrique (§7).

La règle à appliquer est celle de §6.2 :

1. chaque quantité attendue est donnée avec son libellé, dans la même proposition ou ligne de tableau ; un nombre sans libellé ne compte pas ;
2. la valeur est celle du moteur, arrondie aux chiffres écrits, signe compris ; l'unité, si elle est écrite, est celle du moteur ou une
   réécriture exacte ; la dose du tour de rappel exige son unité ;
3. une valeur niée ou désavouée ne compte pas ;
4. deux valeurs différentes pour la même quantité demandée : WRONG, même si l'une est juste ;
5. hors tour 1, plus de 3 quantités non demandées : WRONG ; une valeur interdite : WRONG quel que soit le nombre ;
6. le tour de la demi-vie dit si l'extrapolation est acceptable, et ce verdict est le bon ;
7. rappel : dose avec unité, voie, méthode d'AUC ; comparaison : AUC(0-tlast) lin-up/log-down, différence, pourcentage ; non disponible : dire
   que ce n'est pas calculé, sans valeur étiquetée.

Un tour coupé par la limite d'outils ou une réponse sans valeur quand on en attendait une est `WRONG`.

"""

def cmd_sample():
    picks, sizes = draw()
    os.makedirs(LABELLING, exist_ok=True)
    L = [SHEET_HEAD.format(n=len(picks), per=SAMPLE_PER_KIND, seed=SAMPLE_SEED)]
    for p in picks:
        question, kind, expected, answer = _expected(p)
        L += [f"---\n\n## {p['id']}\n", f"**Question.** {question}\n", "**Attendu (gold).**\n", *expected, "", "**Réponse montrée à l'utilisateur.**\n", "````text", answer, "````\n"]
    with open(os.path.join(LABELLING, "SHEET.md"), "w", encoding="utf-8", newline="\n") as f: f.write("\n".join(L))
    with open(os.path.join(LABELLING, "sample.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"seed": SAMPLE_SEED, "per_kind": SAMPLE_PER_KIND, "pool": sizes, "turns": picks}, f, ensure_ascii=False, indent=1); f.write("\n")
    path = os.path.join(LABELLING, "labels.csv")
    if not os.path.exists(path):                          # never overwrites labels already written
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n"); w.writerow(("id", "label", "note")); w.writerows((p["id"], "", "") for p in picks)
    print("written", LABELLING, "pool per kind:", sizes)

def cmd_agreement():
    with open(os.path.join(LABELLING, "sample.json"), encoding="utf-8") as f: picks = {p["id"]: p for p in json.load(f)["turns"]}
    with open(os.path.join(LABELLING, "labels.csv"), encoding="utf-8", newline="") as f: rows = list(csv.DictReader(f))
    bad = [r["id"] for r in rows if r["label"].strip().upper() not in LABELS]
    if bad: raise SystemExit("not labelled: " + ", ".join(bad))
    agree, out = 0, []
    for row in rows:
        p = picks[row["id"]]; r, t = _stored_turn(p)
        meta, text, script = gold(p["gold"], p["exercise"])
        k = p["turn"] - 1
        outcome, rub = judge(score, t, script[k], meta, text, r["turns"][:k])
        human, machine = row["label"].strip().upper(), "CORRECT" if outcome == "CORRECT" else "WRONG"
        agree += human == machine
        if human != machine: out.append(f"{row['id']} {p['config']} seed {p['seed']} {p['exercise']} t{p['turn']}: Abdou {human}, rubric {outcome} "
                                        f"({'; '.join((rub or {}).get('reasons', [])) or 'no reason'}) {row['note']}".rstrip())
    print(f"agreement before resolution: {agree} / {len(rows)}")
    print("\n".join(out))

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("rescore"); p.add_argument("--before", default="main")
    sub.add_parser("sample"); sub.add_parser("agreement")
    a = ap.parse_args()
    if a.cmd == "rescore": cmd_rescore(a.before)
    elif a.cmd == "sample": cmd_sample()
    else: cmd_agreement()

if __name__ == "__main__":
    main()
