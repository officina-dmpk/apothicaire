#!/usr/bin/env python
"""Training data of the decision model (D-01, step 1): rows in the typed-decisions format of Unsloth.

  python decision/make_dataset.py [--out decision/data] [--no-readme]

One row = one state and seven closed questions, with their gold answers (schema of the Hugging Face dataset
`LocalLLaMA/typed-decisions`, subset `all`, recorded in decision/README.md): id, workflow, split, state, questions, gold, factors,
label_agreement, n_questions; the five last-but-one fields are JSON strings. Writes data/train.jsonl and data/heldout.jsonl.

The state is a text digest of what the harness will know at that point of the conversation: the header and first rows of the CSV, the
dose / route / units sentence as the user wrote it, the analyses already in the project (id, kind, AUC method), the note on BLQ values,
and the request of the turn. The gold answers come from the truth: bench-style meta.json (route, dose unit, parameters not computed
for the route) and the intent of the turn kind (bench/scripts.py: 8 scripted kinds, plus 4 extra kinds written here). Paraphrases of the
questions are written by hand (WORDINGS), never by a model. No engine is needed to build the dataset, only the exercise folders:
bench/exercises/ (the 25 of the benchmark) and decision/exercises/ (75 more, decision/make_exercises.py).

The split is by exercise: HELDOUT_N whole exercises, drawn with SPLIT_SEED among the exercises that are not in the benchmark, go to
heldout.jsonl; the benchmark exercises and the rest go to train.jsonl (the benchmark exercises carry factors.bench = true).
"""
import argparse, collections, json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
if AGENT not in sys.path: sys.path.insert(0, AGENT)
from bench import make_exercises as mk, scripts  # noqa: E402

BENCH_DIR = os.path.join(AGENT, "bench", "exercises")
EXTRA_DIR = os.path.join(HERE, "exercises")
OUT = os.path.join(HERE, "data")
README = os.path.join(HERE, "README.md")
SPLIT_SEED, HELDOUT_N = 20261010, 20
ROW_SEED = 7
WORKFLOW = "pk_analysis_requests"
EXTRA_KINDS = ("nca_other", "fit_pk1", "fit_pk2", "simulate")
KINDS = scripts.KINDS + EXTRA_KINDS
PARAPHRASES_PER_KIND = 2          # plus the scripted wording for the 8 scripted kinds
P_UNIT_OMITTED, P_ROUTE_OMITTED, P_LATE = 0.2, 0.2, 0.4
COUNTS_BEGIN, COUNTS_END = "<!-- counts:begin -->", "<!-- counts:end -->"

# ---------------------------------------------------------------- the closed questions
ANALYSES = {"nca": "Run a new non-compartmental analysis (NCA) on the imported data.",
            "fit_pk1": "Fit a one-compartment model to the data.",
            "fit_pk2": "Fit a two-compartment model to the data.",
            "simulate": "Simulate a concentration profile from a model that is already fitted.",
            "compare": "Compare two analyses of the project (the second one has been run for this request).",
            "none_needed": "No new computation: answer from the analyses already in the project or from what the user said."}
ROUTES = {"iv_bolus": "Intravenous bolus.", "iv_infusion": "Intravenous infusion.", "oral": "Oral (extravascular) administration.",
          "unknown": "The user did not state the route."}
AUC_METHODS = {"linear": "Linear trapezoidal rule.", "lin_up_log_down": "Linear up, logarithmic down.",
               "not_applicable": "The request names no AUC method and runs no NCA."}
PARAMETERS = {"cmax": "Cmax only.", "tmax": "Tmax only.", "c0": "C0 (extrapolated initial concentration) only.",
              "auclast": "AUC(0-tlast) only.", "aucinf": "AUC(0-inf) only.", "lambda_z": "The terminal rate constant lambda_z only.",
              "half_life": "The terminal half-life only.", "cl": "The clearance (CL or CL/F) only.",
              "vz": "The volume of distribution (Vz or Vz/F) only.", "mrt": "The mean residence time only.",
              "aucpext": "The percentage of the AUC extrapolated to infinity only.",
              "lambda_z_points": "The number of points of the lambda_z regression only.",
              "adj_r2": "The adjusted R squared of the lambda_z regression only.", "tlag": "The lag time only.",
              "several": "Two or more parameters, or all the parameters of a model.",
              "none": "No parameter value: a recall, a simulation, a comparison of methods without a named parameter."}
TF = {"false": "No.", "true": "Yes."}

def questions_for(analysis_ids):
    """The closed set of seven questions for a state whose project holds the analyses `analysis_ids` (sorted ids)."""
    pairs = {f"{a}+{b}": f"Compare analysis {a} with analysis {b}." for i, a in enumerate(analysis_ids) for b in analysis_ids[i + 1:]}
    pair_options = {"not_applicable": "The request compares no analyses.", **(pairs or {"none_available": "Fewer than two analyses exist, so no pair can be compared."})}
    return {
        "analysis": {"type": "choice", "instructions": "Which computation does the last request of the user need, given the analyses already in the project?", "criteria": ANALYSES},
        "route": {"type": "choice", "instructions": "Which administration route did the user state for the dose?", "criteria": ROUTES},
        "auc_method": {"type": "choice", "instructions": "Which AUC integration method does the last request specify or require for the analysis to run?", "criteria": AUC_METHODS},
        "parameter_asked": {"type": "choice", "instructions": "Which pharmacokinetic parameter does the last request ask for?", "criteria": PARAMETERS},
        "dose_has_unit": {"type": "noul", "instructions": "The dose stated by the user carries a unit (mg, ug, ...).", "criteria": TF},
        "is_not_available": {"type": "noul", "instructions": "The last request asks for a parameter that Caladrius does not compute for the stated route.", "criteria": TF},
        "compare_pair": {"type": "choice", "instructions": "Which two analyses of the project does the last request ask to compare?", "criteria": pair_options}}

def gold_choice(options, label):
    assert label in options, (label, list(options))
    return {"confidence": 1.0, "label": label, "probabilities": {k: 1.0 if k == label else 0.0 for k in options}, "type": "choice"}

def gold_noul(flag):
    return {"confidence": 1.0, "label": "true" if flag else "false", "noul": 1.0 if flag else 0.0,
            "probabilities": {"false": 0.0 if flag else 1.0, "true": 1.0 if flag else 0.0}, "type": "noul"}

# ---------------------------------------------------------------- hand-written French wordings
# (text, parameters asked). {cl} / {vz}: CL, Vz (CL/F, Vz/F after an oral dose). The scripted wording of each kind comes from
# bench/scripts.py and is not repeated here. Parameters asked: keys of PARAMETERS; one key => that key, several => "several".
WORDINGS = {
    "import_nca": [
        ("Lance une NCA (trapèzes linéaires) et rapporte-moi Cmax, Tmax, les deux AUC, λz, la demi-vie, {cl}, {vz} et le MRT avec leurs unités.", ["many"]),
        ("Peux-tu analyser ces données en non-compartimental, AUC par la méthode linéaire, et me donner les paramètres usuels (Cmax, Tmax, AUC, λz, t½, {cl}, {vz}, MRT) ?", ["many"]),
        ("NCA s'il te plaît, trapèzes linéaires. J'attends Cmax, Tmax, AUC0-t, AUC0-inf, lambda z, demi-vie, clairance, volume de distribution et MRT.", ["many"]),
        ("Analyse non compartimentale de ce profil avec la méthode des trapèzes linéaires : tous les paramètres standards, avec leurs unités.", ["many"])],
    "cmax_tmax_bolus": [
        ("Donne-moi la concentration initiale extrapolée, ainsi que le pic observé et son temps.", ["c0", "cmax", "tmax"]),
        ("Quelle est la concentration extrapolée à t = 0 ?", ["c0"]),
        ("Cmax et Tmax, s'il te plaît.", ["cmax", "tmax"]),
        ("Quelle est la concentration maximale observée ?", ["cmax"]),
        ("C0, Cmax et Tmax avec leurs unités.", ["c0", "cmax", "tmax"])],
    "cmax_tmax": [
        ("Quelle est la concentration maximale et à quel moment est-elle atteinte ?", ["cmax", "tmax"]),
        ("Donne-moi Cmax et Tmax.", ["cmax", "tmax"]),
        ("Quel est le pic de concentration, et à quel temps ?", ["cmax", "tmax"]),
        ("Je voudrais la Cmax observée avec son unité.", ["cmax"]),
        ("À quel temps la concentration est-elle maximale (Tmax) ?", ["tmax"])],
    "clearance_volume": [
        ("Quelle est la clairance ({cl}) et le volume de distribution ({vz}) ? Unités comme dans le rapport de Caladrius.", ["cl", "vz"]),
        ("Et la clairance, avec son unité ?", ["cl"]),
        ("Je veux {cl} et {vz}, dans les unités de Caladrius, sans conversion.", ["cl", "vz"]),
        ("Quel est le volume apparent de distribution {vz} ?", ["vz"]),
        ("Clairance et volume, s'il te plaît, tels quels.", ["cl", "vz"])],
    "half_life": [
        ("Donne-moi la demi-vie terminale.", ["half_life"]),
        ("Quel est le t½ et la part de l'AUC extrapolée jusqu'à l'infini ?", ["half_life", "aucpext"]),
        ("La part extrapolée de l'AUC est-elle acceptable ? Donne le pourcentage.", ["aucpext"]),
        ("Combien de temps faut-il pour que la concentration terminale soit divisée par deux ?", ["half_life"]),
        ("Demi-vie et pourcentage d'AUC extrapolé, avec ton avis sur la qualité.", ["half_life", "aucpext"])],
    "lambda_z_regression": [
        ("Sur combien de points la pente terminale a-t-elle été estimée ?", ["lambda_z_points"]),
        ("Quel est le R² ajusté de la régression terminale ?", ["adj_r2"]),
        ("Donne-moi le nombre de points de la régression de lambda z et son R² ajusté.", ["lambda_z_points", "adj_r2"]),
        ("Je voudrais juger la qualité de λz : combien de points, quel R² ?", ["lambda_z_points", "adj_r2"]),
        ("Quel est le nombre de points utilisés pour λz ?", ["lambda_z_points"])],
    "recall": [
        ("Peux-tu me redire la dose, la voie et la méthode d'AUC que j'avais données au début ?", []),
        ("Rappelle-moi ce que j'ai indiqué comme dose et voie d'administration, et quelle méthode d'AUC on a utilisée.", []),
        ("Quelle dose ai-je renseignée au départ, et par quelle voie ?", []),
        ("Résume les réglages de départ : dose, voie, méthode d'AUC.", []),
        ("Je ne me souviens plus de la dose ni de la voie d'administration que je t'ai indiquées.", [])],
    "compare": [
        ("Relance avec la méthode lin-up/log-down et compare l'AUC(0-tlast) avec la méthode linéaire : écart absolu et en pourcentage ?", ["auclast"]),
        ("Quelle différence y a-t-il entre l'AUC(0-tlast) en trapèzes linéaires et en linear-up/log-down ? Donne l'écart et le pourcentage.", ["auclast"]),
        ("Refais le calcul avec linear-up/log-down puis compare les deux AUC(0-tlast), en valeur et en %.", ["auclast"]),
        ("Compare les deux méthodes d'AUC, linéaire et lin-up/log-down, sur l'AUC(0-tlast).", ["auclast"]),
        ("Et si on utilisait lin-up/log-down ? De combien change l'AUC(0-tlast) par rapport à la méthode linéaire ?", ["auclast"])],
    "not_available_oral": [
        ("Donne-moi la concentration extrapolée à l'instant zéro (C0).", ["c0"]),
        ("Quelle est la valeur de C0 ?", ["c0"]),
        ("Je voudrais C0, la concentration initiale extrapolée.", ["c0"]),
        ("Quelle était la concentration initiale C0 extrapolée à t = 0 ?", ["c0"])],
    "not_available_iv": [
        ("Quel est le Tlag ?", ["tlag"]),
        ("Donne-moi le temps de latence.", ["tlag"]),
        ("Y a-t-il un temps de latence ? Quelle valeur ?", ["tlag"]),
        ("Quelle est la valeur du temps de latence Tlag ?", ["tlag"])],
    "not_available_infusion": [
        ("Quel est le Tlag ?", ["tlag"]),
        ("Donne-moi le temps de latence.", ["tlag"]),
        ("Quelle est la concentration extrapolée à t = 0 (C0) ?", ["c0"]),
        ("Quelle est la valeur de C0 ?", ["c0"])],
    # extra kinds (not in bench/scripts.py): single parameters read from the NCA already run, fits, simulation
    "nca_other": [
        ("Quelle est l'AUC(0-inf) ?", ["aucinf"]),
        ("Donne-moi le MRT.", ["mrt"]),
        ("Quelle est l'AUC(0-tlast) ?", ["auclast"]),
        ("Donne-moi λz avec son unité.", ["lambda_z"]),
        ("Quelle est l'AUC jusqu'à l'infini et quel est le MRT ?", ["aucinf", "mrt"])],
    "fit_pk1": [
        ("Ajuste un modèle à un compartiment sur ces données.", ["many"]),
        ("Peux-tu faire un fit mono-compartimental ?", ["many"]),
        ("Fais une régression non linéaire avec un modèle à un compartiment et donne-moi les paramètres.", ["many"]),
        ("Je veux ajuster un modèle PK à 1 compartiment (clairance, volume).", ["many"])],
    "fit_pk2": [
        ("Ajuste un modèle à deux compartiments sur ces données.", ["many"]),
        ("Peux-tu faire un fit bicompartimental ?", ["many"]),
        ("Fais une régression non linéaire avec un modèle à deux compartiments et donne-moi les paramètres.", ["many"]),
        ("Je veux ajuster un modèle PK à 2 compartiments (CL, Vc, Q, Vp).", ["many"])],
    "simulate": [
        ("Simule le profil attendu avec les paramètres du modèle ajusté.", []),
        ("Peux-tu simuler la concentration avec le modèle ajusté ?", []),
        ("Fais une simulation à partir du fit.", []),
        ("Trace la courbe prédite par le modèle ajusté.", [])]}

# user's introduction of the data (turn 1): {dr} = dose + route as one phrase, {t} / {c}: time and concentration units
INTROS = [
    "Voilà mes mesures : {dr} ; le temps est en {t}, la concentration en {c}.",
    "J'ai administré {dr}. Temps en {t}, concentrations en {c}. Données :",
    "Exercice : {dr} ; temps ({t}) et concentration ({c}) ci-dessous.",
    "Voici un profil concentration-temps après {dr} (unités : {t} et {c}) :",
    "Données de l'étudiant : {dr}, temps en {t}, concentrations en {c} :"]
ROUTE_PHRASES = {"oral": ["par voie orale", "per os", "en prise orale"],
                 "iv_bolus": ["en bolus intraveineux", "en bolus IV", "en injection intraveineuse rapide"],
                 "iv_infusion": ["en perfusion intraveineuse de {d} {t}", "en perfusion IV de {d} {t}", "en perfusion de {d} {t} par voie intraveineuse"]}
BLQ_NOTES = ["Les 0 correspondent à des valeurs sous la LLOQ ({l} {c}).", "Attention : les concentrations nulles sont en dessous de la limite de quantification, LLOQ = {l} {c}.",
             "LLOQ = {l} {c} ; un 0 veut dire « non quantifiable »."]
# regexes used to check, independently of the generator, what a dose sentence says (tests)
UNIT_RE = r"\d\s*(?:mg|µg|μg|ug)\b"
ROUTE_RE = {"oral": r"orale?\b|per os", "iv_bolus": r"bolus|injection intraveineuse rapide", "iv_infusion": r"perfusion"}

# ---------------------------------------------------------------- gold of the scripted intents
ANALYSIS_OF = {"import_nca": "nca", "cmax_tmax": "none_needed", "clearance_volume": "none_needed", "half_life": "none_needed",
               "lambda_z_regression": "none_needed", "recall": "none_needed", "compare": "compare", "not_available": "none_needed",
               "nca_other": "none_needed", "fit_pk1": "fit_pk1", "fit_pk2": "fit_pk2", "simulate": "simulate"}
AUC_METHOD_OF = {"import_nca": "linear", "compare": "lin_up_log_down"}            # every other kind: not_applicable

def scripted_params(kind, route_kind, what):
    """Parameters asked by the scripted wording of a kind."""
    return {"import_nca": ["many"], "cmax_tmax": ["c0", "cmax", "tmax"] if route_kind == "iv_bolus" else ["cmax", "tmax"],
            "clearance_volume": ["cl", "vz"], "half_life": ["half_life", "aucpext"], "lambda_z_regression": ["lambda_z_points", "adj_r2"],
            "recall": [], "compare": ["auclast"], "not_available": [what]}[kind]

def parameter_label(params):
    return "none" if not params else (params[0] if len(params) == 1 and params[0] != "many" else "several")

def pool_key(kind, route_kind):
    if kind == "cmax_tmax" and route_kind == "iv_bolus": return "cmax_tmax_bolus"
    if kind == "not_available": return {"oral": "not_available_oral", "iv_bolus": "not_available_iv", "iv_infusion": "not_available_infusion"}[route_kind]
    return kind

# ---------------------------------------------------------------- exercise folders
def load_exercises():
    """[(meta, csv, in_benchmark)] sorted by id: the benchmark's 25 and the decision/exercises ones."""
    out = []
    for root, bench in ((BENCH_DIR, True), (EXTRA_DIR, False)):
        if not os.path.isdir(root): continue
        for d in mk.list_exercises(root):
            meta, csv = mk.load(d)
            out.append((meta, csv, bench))
    assert len({m["id"] for m, _, _ in out}) == len(out), "duplicate exercise ids"
    return sorted(out, key=lambda x: x[0]["id"])

def split_ids(exercises):
    """(train ids, heldout ids): HELDOUT_N exercises drawn with SPLIT_SEED among those that are not in the benchmark."""
    new = sorted(m["id"] for m, _, bench in exercises if not bench)
    held = set(random.Random(SPLIT_SEED).sample(new, HELDOUT_N))
    return sorted(m["id"] for m, _, _ in exercises if m["id"] not in held), sorted(held)

# ---------------------------------------------------------------- one row
def route_phrase(meta, rng):
    kind = scripts.kind_of(meta)
    d = scripts.fr(meta["route"]["iv_infusion"]["duration"]) if kind == "iv_infusion" else ""
    return rng.choice(ROUTE_PHRASES[kind]).format(d=d, t=meta["units"]["time"])

def build_row(meta, csv, bench, kind, j, wording, rng):
    """One state with its seven questions. `wording` is None for the scripted wording of a scripted kind (j = 0), else the index of a
    hand-written paraphrase in WORDINGS[pool_key(kind, route)]."""
    route_kind = scripts.kind_of(meta); u = meta["units"]
    script = {t["kind"]: t for t in scripts.build_script(meta, csv)}
    what = script["not_available"]["expect"]["not_calculated_parameter"]
    assert what in meta["ground_truth"]["nca"]["linear"]["not_calculated"], (meta["id"], what)
    cl, vz = ("CL/F", "Vz/F") if route_kind == "oral" else ("CL", "Vz")
    scripted = wording is None
    # the dose / route / units sentence of the first message (the scripted one, or a hand-written variant that may omit unit / route)
    t1 = script["import_nca"]["question"].split(chr(10))
    omit_unit = not scripted and rng.random() < P_UNIT_OMITTED
    omit_route = not scripted and kind != "not_available" and rng.random() < P_ROUTE_OMITTED
    intro_variant = -1
    if scripted:
        intro = t1[0]
    else:
        intro_variant = rng.randrange(len(INTROS))
        dose = scripts.fr(meta["dose"]["amount"]) + ("" if omit_unit else " " + scripts.UNIT_FR[meta["dose"]["unit"]])
        dr = dose if omit_route else dose + " " + route_phrase(meta, rng)
        intro = INTROS[intro_variant].format(dr=dr, t=u["time"], c=u["conc"])
    notes = []
    if meta.get("blq"):
        notes.append(t1[-2] if scripted else rng.choice(BLQ_NOTES).format(l=scripts.fr(meta["blq"]["lloq"]), c=u["conc"]))
    # the request of the turn and the parameters it asks
    if scripted:
        request = t1[-1] if kind == "import_nca" else script[kind]["question"]
        params = scripted_params(kind, route_kind, what)
    else:
        text, params = WORDINGS[pool_key(kind, route_kind)][wording]
        request = text.format(cl=cl, vz=vz)
    # analyses already in the project
    late = kind in ("cmax_tmax", "clearance_volume", "half_life", "lambda_z_regression", "recall", "nca_other", "fit_pk1", "fit_pk2") and rng.random() < P_LATE
    a1 = {"id": 2, "kind": "nca", "auc_method": "linear"}
    a2 = {"id": 3, "kind": "nca", "auc_method": "lin_up_log_down"}
    if kind == "import_nca": analyses = []
    elif kind in ("compare", "not_available") or late: analyses = [a1, a2]
    elif kind == "simulate": analyses = [a1, {"id": 3, "kind": "fit_pk2" if meta["family"].startswith("pk2") else "fit_pk1"}]
    else: analyses = [a1]
    rows = csv.strip().splitlines()
    state = {"analyses": analyses, "data": {"first_rows": rows[1:6], "header": rows[0], "n_rows": len(rows) - 1, "n_subjects": 1},
             "notes": notes, "request": request, "user_dose_sentence": intro}
    ids = sorted(a["id"] for a in analyses)
    qs = questions_for(ids)
    pair = f"{ids[0]}+{ids[1]}" if kind == "compare" else "not_applicable"
    gold = {"analysis": gold_choice(qs["analysis"]["criteria"], ANALYSIS_OF[kind]),
            "route": gold_choice(ROUTES, "unknown" if omit_route else route_kind),
            "auc_method": gold_choice(AUC_METHODS, AUC_METHOD_OF.get(kind, "not_applicable")),
            "parameter_asked": gold_choice(PARAMETERS, parameter_label(params)),
            "dose_has_unit": gold_noul(not omit_unit),
            "is_not_available": gold_noul(kind == "not_available"),
            "compare_pair": gold_choice(qs["compare_pair"]["criteria"], pair)}
    assert set(gold) == set(qs)
    factors = {"exercise": meta["id"], "family": meta["family"], "kind": kind, "route": route_kind, "scripted_wording": scripted,
               "scripted_kind": kind in scripts.KINDS, "bench": bench, "wording": j, "intro_variant": intro_variant,
               "dose_unit_omitted": omit_unit, "route_omitted": omit_route, "late_state": bool(late), "n_analyses": len(analyses),
               "blq": bool(meta.get("blq")), "dose_unit": meta["dose"]["unit"], "parameters_asked": params}
    agreement = {q: {"argmax_agree": True, "argmax_majority": g["label"], "total_variation": 0.0} for q, g in gold.items()}
    dump = lambda o: json.dumps(o, ensure_ascii=False, sort_keys=True)
    return {"id": None, "workflow": WORKFLOW, "split": None, "state": dump(state), "questions": dump(qs), "gold": dump(gold),
            "factors": dump(factors), "label_agreement": dump(agreement), "n_questions": len(qs)}

def exercise_rows(meta, csv, bench):
    """All rows of an exercise: per kind the scripted wording (scripted kinds) and PARAPHRASES_PER_KIND distinct paraphrases
    (one more for the extra kinds, which have no scripted wording)."""
    route_kind = scripts.kind_of(meta); out = []
    for kind in KINDS:
        scripted_kind = kind in scripts.KINDS
        pool = WORDINGS[pool_key(kind, route_kind)]
        pick = random.Random(f"{ROW_SEED}:{meta['id']}:{kind}:pick").sample(range(len(pool)), PARAPHRASES_PER_KIND + (0 if scripted_kind else 1))
        for j, w in enumerate(([None] if scripted_kind else []) + pick):
            out.append(build_row(meta, csv, bench, kind, j, w, random.Random(f"{ROW_SEED}:{meta['id']}:{kind}:{j}")))
    return out

def build():
    """(train rows, heldout rows) with ids and split filled in; deterministic."""
    exercises = load_exercises()
    _, held = split_ids(exercises); held = set(held)
    train, heldout = [], []
    for meta, csv, bench in exercises:
        (heldout if meta["id"] in held else train).extend(exercise_rows(meta, csv, bench))
    out = []
    for rows, split, pre in ((train, "train", "tr"), (heldout, "test", "te")):
        random.Random(f"{ROW_SEED}:{split}").shuffle(rows)
        for n, r in enumerate(rows):
            r["id"] = f"{pre}_{WORKFLOW}_{n:06d}"; r["split"] = split
        out.append(rows)
    return out[0], out[1]

# ---------------------------------------------------------------- statistics, README block
def stats(train, heldout):
    """Counts: rows, exercises and the histogram of every question's gold label, per file."""
    out = {}
    for name, rows in (("train", train), ("heldout", heldout)):
        hist = collections.defaultdict(collections.Counter)
        ex = set()
        for r in rows:
            ex.add(json.loads(r["factors"])["exercise"])
            for q, g in json.loads(r["gold"]).items(): hist[q][g["label"]] += 1
        out[name] = {"rows": len(rows), "exercises": len(ex), "hist": {q: dict(sorted(c.items())) for q, c in hist.items()}}
    return out

def counts_block(st):
    qs = list(questions_for([2, 3]))
    lines = [COUNTS_BEGIN, "", "| file | rows | exercises |", "|---|---|---|"]
    for name in ("train", "heldout"): lines.append(f"| {name}.jsonl | {st[name]['rows']} | {st[name]['exercises']} |")
    for q in qs:
        labels = sorted(set(st["train"]["hist"][q]) | set(st["heldout"]["hist"][q]))
        lines += ["", f"`{q}`", "", "| answer | train | heldout |", "|---|---|---|"]
        lines += [f"| {l} | {st['train']['hist'][q].get(l, 0)} | {st['heldout']['hist'][q].get(l, 0)} |" for l in labels]
    lines += ["", COUNTS_END]
    return "\n".join(lines)

def update_readme(block, path=README):
    if not os.path.isfile(path): return False
    with open(path, encoding="utf-8") as f: text = f.read()
    if COUNTS_BEGIN not in text: return False
    new = re.sub(re.escape(COUNTS_BEGIN) + r".*?" + re.escape(COUNTS_END), lambda _: block, text, flags=re.S)
    with open(path, "w", encoding="utf-8", newline="\n") as f: f.write(new)
    return True

def write(rows, path):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=OUT); ap.add_argument("--no-readme", action="store_true")
    a = ap.parse_args()
    train, heldout = build()
    os.makedirs(a.out, exist_ok=True)
    write(train, os.path.join(a.out, "train.jsonl")); write(heldout, os.path.join(a.out, "heldout.jsonl"))
    st = stats(train, heldout)
    if not a.no_readme: update_readme(counts_block(st))
    print(json.dumps({k: {"rows": v["rows"], "exercises": v["exercises"]} for k, v in st.items()}))
