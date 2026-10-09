#!/usr/bin/env python
"""Training data of the decision model (D-01, step 1), dataset v2 (2026-10-10): rows in the typed-decisions format of Unsloth.

  python decision/make_dataset.py [--out decision/data] [--no-readme]

One row = one state and its closed questions, with their gold answers (schema of the Hugging Face dataset
`LocalLLaMA/typed-decisions`, subset `all`, recorded in decision/README.md): id, workflow, split, state, questions, gold, factors,
label_agreement, n_questions; the five last-but-one fields are JSON strings.

The state is a text digest of what the harness will know at that point of the conversation: the header and first rows of the CSV, the
dose / route / units sentence as the user wrote it, the analyses already in the project (id, kind, AUC method), the note on BLQ values,
and the request of the turn. The gold answers come from the truth and from declared intents, never from a pattern over the text:
meta.json (route, dose, parameters not computed for the route), the turn kind (bench/scripts.py: 8 scripted kinds, plus 7 kinds
written here) and the intent each hand-written wording declares in decision/wordings.json (parameters asked, AUC method, whether a
one-line first message gives a dose and a route), plus the generator's own draws (dose written with its unit, in another unit or
without a unit; route phrase omitted). No engine is needed, only the exercise folders: bench/exercises/ (the 25 of the benchmark) and
decision/exercises/ (75 more, decision/make_exercises.py).

Two splits (v2). By exercise: the 25 benchmark exercises go to bench.jsonl (never used for training or calibration); of the 75 new ones,
HELDOUT_N whole ones drawn with SPLIT_SEED are held out. By wording: in every pool of decision/wordings.json about a quarter of the
wordings (WORDING_HELDOUT_SHARE, drawn with WORDING_SEED) is held out and never appears in a train row; the scripted wording of the
benchmark (bench/scripts.py) is always on the train side. Files: train.jsonl (train exercises, train wordings), heldout_exercises.jsonl
(held-out exercises, train wordings), heldout_wordings.jsonl (train exercises, held-out wordings), heldout_both.jsonl (held-out
exercises, held-out wordings), bench.jsonl (benchmark exercises, train wordings).
"""
import argparse, collections, json, os, random, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
if AGENT not in sys.path: sys.path.insert(0, AGENT)
from bench import make_exercises as mk, scripts  # noqa: E402

BENCH_DIR = os.path.join(AGENT, "bench", "exercises")
EXTRA_DIR = os.path.join(HERE, "exercises")
OUT = os.path.join(HERE, "data")
README = os.path.join(HERE, "README.md")
WORDINGS_FILE = os.path.join(HERE, "wordings.json")
OOD_REQUESTS = os.path.join(HERE, "ood", "requests.jsonl")
SPLIT_SEED, HELDOUT_N = 20261010, 20
WORDING_SEED, WORDING_HELDOUT_SHARE = 20261011, 0.25
ROW_SEED = 7
WORKFLOW = "pk_analysis_requests"
EXTRA_KINDS = ("nca_other", "fit_pk1", "fit_pk2", "simulate", "nca_oneline", "compare_directed", "not_supported")
KINDS = scripts.KINDS + EXTRA_KINDS
SLOT_KINDS = ("intro", "route_oral", "route_iv_bolus", "route_iv_infusion", "blq_note")
# rows per (exercise, kind) besides the scripted wording (scripted kinds only): train side, then the held-out-wording files
PARAPHRASES = {**{k: 2 for k in scripts.KINDS}, **{k: 3 for k in EXTRA_KINDS}, "nca_oneline": 4}
HELDOUT_WORDING_ROWS = {"heldout_wordings": 1, "heldout_both": 2}
DOSE_FILLS = (("unit", 0.6), ("other_unit", 0.2), ("no_unit", 0.2))   # how a paraphrased dose is written
P_ROUTE_OMITTED, P_LATE, P_FIRST = 0.2, 0.4, 0.3
FIRST_KINDS = ("not_available", "not_supported", "fit_pk1", "fit_pk2")   # may come as the first message (no analysis yet)
LATE_KINDS = ("cmax_tmax", "clearance_volume", "half_life", "lambda_z_regression", "recall", "nca_other", "fit_pk1", "fit_pk2", "not_supported")
CONCRETE_ROUTES = ("oral", "iv_bolus", "iv_infusion")
METHOD_FR = {"linear": "linéaire", "lin_up_log_down": "lin-up/log-down"}
FILES = ("train", "heldout_exercises", "heldout_wordings", "heldout_both", "bench")
HELDOUT_FILES = ("heldout_exercises", "heldout_wordings", "heldout_both")
COUNTS_BEGIN, COUNTS_END = "<!-- counts:begin -->", "<!-- counts:end -->"
WORDINGS_BEGIN, WORDINGS_END = "<!-- wordings:begin -->", "<!-- wordings:end -->"
NEAR_DUPLICATE_JACCARD = 0.6

# ---------------------------------------------------------------- the closed questions
ANALYSES = {"nca": "Run a new non-compartmental analysis (NCA) on the imported data.",
            "fit_pk1": "Fit a one-compartment model to the data.",
            "fit_pk2": "Fit a two-compartment model to the data.",
            "simulate": "Simulate a concentration profile from a model that is already fitted.",
            "compare": "Compare two analyses of the project (the second one has been run for this request).",
            "none_needed": "No new computation: answer from the analyses already in the project or from what the user said.",
            "not_supported": ("Something the harness cannot do (bioequivalence, population or steady-state modelling, urine data, a "
                              "parameter outside the list, a written explanation): nothing is computed and the user is told so.")}
ROUTES = {"iv_bolus": "Intravenous bolus.", "iv_infusion": "Intravenous infusion.", "oral": "Oral (extravascular) administration.",
          "unknown": "The user did not state the route."}
AUC_METHODS = {"linear": "Linear trapezoidal rule.", "lin_up_log_down": "Linear up, logarithmic down.",
               "not_applicable": "The request names no AUC method and runs no NCA."}
# parameter key -> how the question `asked_<key>` names it ("The last request asks for ...")
PARAMETERS = {"cmax": "the observed maximum concentration (Cmax)", "tmax": "the time of the maximum concentration (Tmax)",
              "c0": "the extrapolated initial concentration (C0)", "auclast": "the area under the curve up to the last point, AUC(0-tlast)",
              "aucinf": "the area under the curve extrapolated to infinity, AUC(0-inf)",
              "lambda_z": "the terminal rate constant (lambda_z)", "half_life": "the terminal half-life",
              "cl": "the clearance (CL or CL/F)", "vz": "the volume of distribution (Vz or Vz/F)", "mrt": "the mean residence time (MRT)",
              "aucpext": "the percentage of the AUC extrapolated to infinity",
              "lambda_z_points": "the number of points of the lambda_z regression",
              "adj_r2": "the adjusted R squared of the lambda_z regression", "tlag": "the lag time (Tlag)"}
# the nine parameters the scripted first request names (bench/scripts.py): Cmax, Tmax, AUC(0-tlast), AUC(0-inf), lambda_z, t1/2, CL, Vz, MRT
NCA_USUAL = ["cmax", "tmax", "auclast", "aucinf", "lambda_z", "half_life", "cl", "vz", "mrt"]
TF = {"false": "No.", "true": "Yes."}

def questions_for(analysis_ids):
    """The closed set of questions (6 + one per parameter of PARAMETERS) for a state whose project holds the analyses `analysis_ids` (sorted ids).
    A pair is directed: "a+b" compares b with a as the reference (b minus a), so both orders of two analyses are offered."""
    pairs = {f"{a}+{b}": f"Compare analysis {b} with analysis {a} as the reference (b minus a)."
             for a in analysis_ids for b in analysis_ids if a != b}
    pair_options = {"not_applicable": "The request compares no analyses.", **(pairs or {"none_available": "Fewer than two analyses exist, so no pair can be compared."})}
    return {
        "analysis": {"type": "choice", "instructions": "Which computation does the last request of the user need, given the analyses already in the project?", "criteria": ANALYSES},
        "route": {"type": "choice", "instructions": "Which administration route did the user state for the dose?", "criteria": ROUTES},
        "auc_method": {"type": "choice", "instructions": "Which AUC integration method does the last request specify or require for the analysis to run?", "criteria": AUC_METHODS},
        **{f"asked_{k}": {"type": "noul", "instructions": f"The last request asks for {phrase}.", "criteria": TF} for k, phrase in PARAMETERS.items()},
        "dose_has_unit": {"type": "noul", "instructions": "The dose stated by the user carries a unit (mg, ug, ...).", "criteria": TF},
        "is_not_available": {"type": "noul", "instructions": "The last request asks for a parameter that Caladrius does not compute for the stated route.", "criteria": TF},
        "compare_pair": {"type": "choice", "instructions": "Which two analyses of the project does the last request ask to compare, and in which order (the first one is the reference)?", "criteria": pair_options}}

def gold_choice(options, label):
    assert label in options, (label, list(options))
    return {"confidence": 1.0, "label": label, "probabilities": {k: 1.0 if k == label else 0.0 for k in options}, "type": "choice"}

def gold_noul(flag):
    return {"confidence": 1.0, "label": "true" if flag else "false", "noul": 1.0 if flag else 0.0,
            "probabilities": {"false": 0.0 if flag else 1.0, "true": 1.0 if flag else 0.0}, "type": "noul"}

# ---------------------------------------------------------------- hand-written French wordings (decision/wordings.json)
# The scripted wording of each scripted kind comes from bench/scripts.py and is not in the file. The parameters a wording asks are the
# keys of PARAMETERS it names (the gold of the questions `asked_<key>`); [] for a recall, a simulation, the fits (their parameters are
# model parameters, not the NCA parameters of PARAMETERS) and an out-of-scope request.
REQUEST_SLOTS = {"cl", "vz"}
SLOTS = {"compare_directed": REQUEST_SLOTS | {"ref", "other", "ref_method", "other_method"},
         "oneline": REQUEST_SLOTS | {"dose", "wrong_dose", "route", "d", "t", "c"},
         "intro": {"dr", "t", "c"}, "route_oral": set(), "route_iv_bolus": set(), "route_iv_infusion": {"d", "t"}, "blq_note": {"l", "c"}}
ONELINE_KINDS = ("nca_oneline", "fit_pk1", "fit_pk2", "not_supported")      # kinds whose wordings may be a whole first message

def load_wordings(path=WORDINGS_FILE):
    """{"families": {...}, "kinds": {kind: [wording]}} of decision/wordings.json, checked (validate_wordings)."""
    with open(path, encoding="utf-8") as f: w = json.load(f)
    validate_wordings(w)
    return w

def slots_of(text):
    return set(re.findall(r"\{(\w+)\}", text))

def validate_wordings(w):
    """Raises AssertionError on a malformed wordings file: pools, ids, families, slots, declared intents."""
    assert set(w["kinds"]) == set(KINDS) | set(SLOT_KINDS), sorted(set(w["kinds"]) ^ (set(KINDS) | set(SLOT_KINDS)))
    ids = set()
    for kind, pool in w["kinds"].items():
        for x in pool:
            assert x["id"].startswith(kind + ".") and x["id"] not in ids, x["id"]; ids.add(x["id"])
            assert x["family"] in w["families"], (x["id"], x["family"])
            text = x["text"]; assert text.strip() == text and text, x["id"]
            if kind in SLOT_KINDS:
                assert slots_of(text) <= SLOTS[kind], (x["id"], slots_of(text))
                continue
            assert all(p in PARAMETERS for p in x["asked"]) and len(set(x["asked"])) == len(x["asked"]), x["id"]
            if kind in ("import_nca", "nca_oneline"): assert x.get("auc_method") in ("linear", "lin_up_log_down"), x["id"]
            else: assert "auc_method" not in x, x["id"]
            if x.get("oneline"):
                assert kind in ONELINE_KINDS, x["id"]
                assert x["dose"] in ("slot", "none") and x["route"] in ("slot", "none") + CONCRETE_ROUTES, x["id"]
                assert slots_of(text) <= SLOTS["oneline"], (x["id"], slots_of(text))
                assert ("dose" in slots_of(text)) == (x["dose"] == "slot") and ("route" in slots_of(text)) == (x["route"] == "slot"), x["id"]
                assert ("wrong_dose" in slots_of(text)) <= ("dose" in slots_of(text)), x["id"]
                assert ("d" in slots_of(text)) <= (x["route"] == "iv_infusion"), x["id"]
            else:
                assert kind != "nca_oneline" and not {"dose", "route"} & set(x), x["id"]
                assert slots_of(text) <= SLOTS.get(kind, REQUEST_SLOTS), (x["id"], slots_of(text))
            if kind == "compare_directed": assert slots_of(text) & {"ref", "ref_method"} and slots_of(text) & {"other", "other_method"}, x["id"]
            if kind in ("recall", "fit_pk1", "fit_pk2", "simulate", "not_supported"): assert x["asked"] == [], x["id"]
            if kind == "not_available": assert set(x["asked"]) & {"c0", "tlag"}, x["id"]

_W = load_wordings()
FAMILIES = _W["families"]
WORDINGS = _W["kinds"]                                          # kind -> [wording]
WORDING_BY_ID = {x["id"]: x for pool in WORDINGS.values() for x in pool}

def not_calculated(meta):
    """The keys of PARAMETERS Caladrius does not compute for the exercise's route (C0 after an oral dose or an infusion, Tlag after an IV dose)."""
    nc = meta["ground_truth"]["nca"]["linear"]["not_calculated"]
    return {k for k in ("c0", "tlag") if k in nc}

def compatible(w, kind, route_kind, nc):
    """Can a request wording be used on an exercise of this route? A route the text implies must be the exercise's; the not-available
    kind asks at least one parameter not computed for the route, every other kind asks none."""
    if w.get("route") in CONCRETE_ROUTES and w["route"] != route_kind: return False
    asked = set(w["asked"])
    return bool(asked & nc) if kind == "not_available" else not (asked & nc)

ROUTE_KINDS = {r: f"route_{r}" for r in CONCRETE_ROUTES}
NC_OF_ROUTE = {"oral": {"c0"}, "iv_bolus": {"tlag"}, "iv_infusion": {"c0", "tlag"}}   # checked against meta.json in the tests

def split_wordings(seed=WORDING_SEED, share=WORDING_HELDOUT_SHARE):
    """({kind: {"train": [ids], "heldout": [ids]}}, attempt). In every pool, round(share * size) wordings (at least one) are held out,
    drawn with `seed`; a draw is redrawn (attempt + 1) until (1) for every route, each request kind keeps enough compatible train wordings
    for the train rows (PARAPHRASES) and at least one compatible held-out wording, (2) every family has wordings on both sides, (3) every
    parameter is asked by some held-out wording and by some train wording. Deterministic."""
    for attempt in range(10000):
        out, ok = {}, True
        for kind, pool in WORDINGS.items():
            ids = [x["id"] for x in pool]
            held = set(random.Random(f"{seed}:{attempt}:{kind}").sample(ids, max(1, round(share * len(ids)))))
            out[kind] = {"train": [i for i in ids if i not in held], "heldout": [i for i in ids if i in held]}
            if kind in KINDS:
                for r in CONCRETE_ROUTES:
                    n = {h: sum(compatible(WORDING_BY_ID[i], kind, r, NC_OF_ROUTE[r]) for i in out[kind][h]) for h in ("train", "heldout")}
                    if n["train"] < PARAPHRASES[kind] or n["heldout"] < 1: ok = False
        if not ok: continue
        fam = {h: {WORDING_BY_ID[i]["family"] for k in out for i in out[k][h]} for h in ("train", "heldout")}
        if not fam["train"] == fam["heldout"] == set(FAMILIES): continue
        asked = {h: {p for k in KINDS for i in out[k][h] for p in WORDING_BY_ID[i]["asked"]} for h in ("train", "heldout")}
        if not asked["train"] == asked["heldout"] == set(PARAMETERS): continue
        return out, attempt
    raise RuntimeError("no wording split satisfies the constraints")

HALVES, HALVES_ATTEMPT = split_wordings()

def half_ids(half):
    """Every wording id of one side of the split ("train" or "heldout")."""
    return {i for k in HALVES for i in HALVES[k][half]}

# ---------------------------------------------------------------- near duplicates (the reviewer's requests are a frozen test set)
def normalise(text):
    """Lower case, accents removed, words and numbers only, every number replaced by 0."""
    t = unicodedata.normalize("NFKD", text.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return ["0" if tok.isdigit() else tok for tok in re.findall(r"[a-z0-9]+", t)]

def trigrams(tokens):
    return {tuple(tokens[i:i + 3]) for i in range(len(tokens) - 2)} if len(tokens) >= 3 else {tuple(tokens)}

def jaccard(a, b):
    """Jaccard similarity of the word trigrams of two texts (normalised)."""
    x, y = trigrams(normalise(a)), trigrams(normalise(b))
    return len(x & y) / len(x | y) if x | y else 1.0

def near_duplicate(a, b, threshold=NEAR_DUPLICATE_JACCARD):
    return normalise(a) == normalise(b) or jaccard(a, b) > threshold

def ood_requests(path=OOD_REQUESTS):
    """The request texts of the reviewer's frozen test set (each whole text and each of its lines)."""
    out = []
    if not os.path.isfile(path): return out
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)["request"]
                out += [r] + [l for l in r.split("\n") if l.strip() and l != r]
    return out

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
    """(train ids, heldout ids, bench ids): the benchmark exercises are bench; HELDOUT_N of the new ones, drawn with SPLIT_SEED, are held out."""
    new = sorted(m["id"] for m, _, bench in exercises if not bench)
    held = set(random.Random(SPLIT_SEED).sample(new, HELDOUT_N))
    return (sorted(i for i in new if i not in held), sorted(held), sorted(m["id"] for m, _, bench in exercises if bench))

# ---------------------------------------------------------------- the state (shared with decision/harness.py)
def _is_data_row(line):
    """A CSV row of numbers (the rows of a pasted data table, not its header)."""
    cells = [c.strip() for c in line.split(",")]
    try: return all(c != "" and float(c) is not None for c in cells)
    except ValueError: return False

def split_first_message(text):
    """The parts of a first user message written like the benchmark's (bench/scripts.py, turn 1): {"intro": the dose / route / units
    sentence (first line), "csv": the header line that follows and the numeric rows under it, "notes": the lines between the data and
    the request (the BLQ sentence), "request": the last line}. "csv" is "" when the second line is not followed by a numeric row."""
    lines = text.strip().split(chr(10))
    body = lines[1:-1] if len(lines) > 2 else []
    k = 1
    while k < len(body) and _is_data_row(body[k]): k += 1
    if k == 1: return {"intro": lines[0], "csv": "", "notes": body, "request": lines[-1]}
    return {"intro": lines[0], "csv": chr(10).join(body[:k]), "notes": body[k:], "request": lines[-1]}

def make_state(csv_text, intro, notes, request, analyses):
    """The state of one turn: the header and first five rows of the CSV, its row count, the dose / route / units sentence as the user
    wrote it, the notes (BLQ), the request of the turn, the analyses already in the project ([{"id", "kind", "auc_method"}])."""
    rows = csv_text.strip().splitlines()
    return {"analyses": analyses, "data": {"first_rows": rows[1:6], "header": rows[0], "n_rows": len(rows) - 1, "n_subjects": 1},
            "notes": notes, "request": request, "user_dose_sentence": intro}

# ---------------------------------------------------------------- gold of the intents
ANALYSIS_OF = {"import_nca": "nca", "cmax_tmax": "none_needed", "clearance_volume": "none_needed", "half_life": "none_needed",
               "lambda_z_regression": "none_needed", "recall": "none_needed", "compare": "compare", "not_available": "none_needed",
               "nca_other": "none_needed", "fit_pk1": "fit_pk1", "fit_pk2": "fit_pk2", "simulate": "simulate",
               "nca_oneline": "nca", "compare_directed": "compare", "not_supported": "not_supported"}
# AUC method: the NCA kinds take the method their wording declares (linear when it names none: the method the analysis needs to run);
# the compare turn re-runs with lin-up/log-down; every other kind, including the directed compare of two existing analyses, runs no NCA
AUC_METHOD_OF = {"compare": "lin_up_log_down"}

def scripted_params(kind, route_kind, what):
    """Parameters (keys of PARAMETERS) asked by the scripted wording of a kind."""
    return {"import_nca": list(NCA_USUAL), "cmax_tmax": ["c0", "cmax", "tmax"] if route_kind == "iv_bolus" else ["cmax", "tmax"],
            "clearance_volume": ["cl", "vz"], "half_life": ["half_life", "aucpext"], "lambda_z_regression": ["lambda_z_points", "adj_r2"],
            "recall": [], "compare": ["auclast"], "not_available": [what]}[kind]

def dose_text(meta, fill, factor=1):
    """The dose as a user writes it: `unit` with the exercise's unit, `other_unit` converted (mg -> g from 100 mg, else mg -> µg;
    µg -> mg), `no_unit` the number alone. `factor` scales the amount (the wrong dose of a correction)."""
    amount, unit = meta["dose"]["amount"] * factor, meta["dose"]["unit"]
    if fill == "unit": return f"{scripts.fr(amount)} {scripts.UNIT_FR[unit]}"
    if fill == "no_unit": return scripts.fr(amount)
    assert fill == "other_unit", fill
    if unit == "mg": return f"{scripts.fr(amount / 1000)} g" if amount >= 100 else f"{scripts.fr(amount * 1000)} µg"
    return f"{scripts.fr(amount / 1000)} mg"

def draw_fill(rng):
    x, acc = rng.random(), 0.0
    for fill, p in DOSE_FILLS:
        acc += p
        if x < acc: return fill
    return DOSE_FILLS[-1][0]

def side_pool(kind, half):
    """The wordings of a pool on one side of the wording split."""
    keep = set(HALVES[kind][half])
    return [x for x in WORDINGS[kind] if x["id"] in keep]

def route_phrase(meta, rng, half, after_dose=True):
    """(phrase, wording id) of the exercise's route, from the route pool of the side `half`; participles only right after the dose."""
    kind = scripts.kind_of(meta)
    pool = [x for x in side_pool(ROUTE_KINDS[kind], half) if after_dose or not x.get("after_dose")]
    x = rng.choice(pool)
    d = scripts.fr(meta["route"]["iv_infusion"]["duration"]) if kind == "iv_infusion" else ""
    return x["text"].format(d=d, t=meta["units"]["time"]), x["id"]

_SCRIPTS = {}
def _script(meta, csv):
    if meta["id"] not in _SCRIPTS: _SCRIPTS[meta["id"]] = {t["kind"]: t for t in scripts.build_script(meta, csv)}
    return _SCRIPTS[meta["id"]]

def build_row(meta, csv, bench, kind, j, wording, rng, half="train"):
    """One state with its closed questions. `wording` is None for the scripted wording of a scripted kind (j = 0), else a wording of
    WORDINGS[kind] (or its id). `half`: the side of the wording split the slot wordings (introduction, route phrase, BLQ note) come from."""
    route_kind = scripts.kind_of(meta); u = meta["units"]
    script = _script(meta, csv)
    what = script["not_available"]["expect"]["not_calculated_parameter"]
    assert what in meta["ground_truth"]["nca"]["linear"]["not_calculated"], (meta["id"], what)
    cl, vz = ("CL/F", "Vz/F") if route_kind == "oral" else ("CL", "Vz")
    scripted = wording is None
    w = WORDING_BY_ID[wording] if isinstance(wording, str) else wording
    if not scripted:
        assert w["id"] in HALVES[kind][half] and compatible(w, kind, route_kind, not_calculated(meta)), (meta["id"], w["id"], half)
    first = split_first_message(script["import_nca"]["question"])
    oneline = not scripted and bool(w.get("oneline"))
    # where the turn is: the first message (no analysis yet) or later
    if kind in ("import_nca", "nca_oneline") or oneline: first_turn = True
    elif not scripted and kind in FIRST_KINDS and (kind != "not_available" or len(w["asked"]) == 1): first_turn = rng.random() < P_FIRST
    else: first_turn = False
    late = not first_turn and kind in LATE_KINDS and rng.random() < P_LATE
    # the dose / route sentence: the scripted one, a one-line first message (the wording itself), or an introduction line
    ids = {"intro": None, "route_phrase": None, "blq_note": None}
    d_inf = scripts.fr(meta["route"]["iv_infusion"]["duration"]) if route_kind == "iv_infusion" else ""
    slots = {"cl": cl, "vz": vz, "t": u["time"], "c": u["conc"], "d": d_inf}
    if scripted:
        fill, route_label, intro = "unit", route_kind, first["intro"]
    elif oneline:
        fill = draw_fill(rng) if w["dose"] == "slot" else "none"
        if fill != "none": slots.update(dose=dose_text(meta, fill), wrong_dose=dose_text(meta, fill, 10))
        if w["route"] == "slot":
            slots["route"], ids["route_phrase"] = route_phrase(meta, rng, half, after_dose=bool(re.search(r"\{dose\},? \{route\}", w["text"])))
            route_label = route_kind
        else:
            route_label = "unknown" if w["route"] == "none" else w["route"]          # a route the text implies is the exercise's (compatible)
        intro = None
    else:
        x = rng.choice(side_pool("intro", half)); ids["intro"] = x["id"]
        fill = draw_fill(rng)
        omit_route = kind != "not_available" and rng.random() < P_ROUTE_OMITTED      # on not_available rows the route decides the answer
        dr = dose_text(meta, fill)
        if not omit_route:
            phrase, ids["route_phrase"] = route_phrase(meta, rng, half)
            dr += " " + phrase
        intro = x["text"].format(dr=dr, t=u["time"], c=u["conc"])
        route_label = "unknown" if omit_route else route_kind
    notes = []
    if meta.get("blq"):
        if scripted: notes.append(first["notes"][0])
        else:
            x = rng.choice(side_pool("blq_note", half)); ids["blq_note"] = x["id"]
            notes.append(x["text"].format(l=scripts.fr(meta["blq"]["lloq"]), c=u["conc"]))
    # the request of the turn and the parameters it asks
    ref = other = None
    if kind == "compare_directed":
        ref = rng.choice([2, 3]); other = 5 - ref
        slots.update(ref=ref, other=other, ref_method=METHOD_FR["linear" if ref == 2 else "lin_up_log_down"],
                     other_method=METHOD_FR["linear" if other == 2 else "lin_up_log_down"])
    if scripted:
        request = first["request"] if kind == "import_nca" else script[kind]["question"]
        params = scripted_params(kind, route_kind, what)
    else:
        request = w["text"].format(**slots)
        params = list(w["asked"])
    if intro is None: intro = request                                                 # one line: the request is the dose sentence
    # analyses already in the project
    a1 = {"id": 2, "kind": "nca", "auc_method": "linear"}
    a2 = {"id": 3, "kind": "nca", "auc_method": "lin_up_log_down"}
    if first_turn: analyses = []
    elif kind in ("compare", "compare_directed", "not_available") or late: analyses = [a1, a2]
    elif kind == "simulate": analyses = [a1, {"id": 3, "kind": "fit_pk2" if meta["family"].startswith("pk2") else "fit_pk1"}]
    else: analyses = [a1]
    state = make_state(csv, intro, notes, request, analyses)
    aids = sorted(a["id"] for a in analyses)
    qs = questions_for(aids)
    pair = {"compare": "2+3", "compare_directed": f"{ref}+{other}"}.get(kind, "not_applicable")
    auc = "linear" if scripted and kind == "import_nca" else (w["auc_method"] if kind in ("import_nca", "nca_oneline") else AUC_METHOD_OF.get(kind, "not_applicable"))
    gold = {"analysis": gold_choice(qs["analysis"]["criteria"], ANALYSIS_OF[kind]),
            "route": gold_choice(ROUTES, route_label),
            "auc_method": gold_choice(AUC_METHODS, auc),
            **{f"asked_{k}": gold_noul(k in params) for k in PARAMETERS},
            "dose_has_unit": gold_noul(fill in ("unit", "other_unit")),
            "is_not_available": gold_noul(kind == "not_available"),
            "compare_pair": gold_choice(qs["compare_pair"]["criteria"], pair)}
    assert set(gold) == set(qs) and set(params) <= set(PARAMETERS)
    factors = {"exercise": meta["id"], "family": meta["family"], "kind": kind, "route": route_kind, "scripted_wording": scripted,
               "scripted_kind": kind in scripts.KINDS, "bench": bench, "wording": j, "file": None,
               "wording_id": None if scripted else w["id"], "wording_family": "scripted" if scripted else w["family"],
               "wording_heldout": half == "heldout", "intro_id": ids["intro"], "route_phrase_id": ids["route_phrase"],
               "blq_note_id": ids["blq_note"], "layout": "scripted" if scripted else ("oneline" if oneline else "intro+request"),
               "dose_fill": fill, "dose_unit_omitted": fill in ("no_unit", "none"), "dose_given": fill != "none",
               "route_omitted": route_label == "unknown", "first_turn": first_turn, "late_state": bool(late),
               "n_analyses": len(analyses), "compare_reference": ref, "blq": bool(meta.get("blq")), "dose_unit": meta["dose"]["unit"],
               "parameters_asked": params}
    agreement = {q: {"argmax_agree": True, "argmax_majority": g["label"], "total_variation": 0.0} for q, g in gold.items()}
    return {"id": None, "workflow": WORKFLOW, "split": None, "state": _dump(state), "questions": _dump(qs), "gold": _dump(gold),
            "factors": _dump(factors), "label_agreement": _dump(agreement), "n_questions": len(qs)}

def _dump(o): return json.dumps(o, ensure_ascii=False, sort_keys=True)

def exercise_rows(meta, csv, bench, half="train", per_kind=None, scripted=True):
    """Rows of an exercise: per kind the scripted wording (scripted kinds, when `scripted`) and `per_kind` distinct wordings of the side
    `half` of the wording split that fit the exercise (default PARAPHRASES[kind]; an int applies to every kind)."""
    route_kind, nc = scripts.kind_of(meta), not_calculated(meta)
    out = []
    for kind in KINDS:
        n = PARAPHRASES[kind] if per_kind is None else per_kind
        pool = [x for x in side_pool(kind, half) if compatible(x, kind, route_kind, nc)]
        assert len(pool) >= (n if half == "train" else 1), (meta["id"], kind, half, len(pool))
        pick = random.Random(f"{ROW_SEED}:{meta['id']}:{kind}:{half}:pick").sample(pool, min(n, len(pool)))
        for j, w in enumerate(([None] if scripted and kind in scripts.KINDS else []) + pick):
            out.append(build_row(meta, csv, bench, kind, j, w, random.Random(f"{ROW_SEED}:{meta['id']}:{kind}:{half}:{j}"), half))
    return out

def build():
    """The rows of FILES (train, heldout_exercises, heldout_wordings, heldout_both, bench), ids and split filled in; deterministic."""
    exercises = load_exercises()
    _, held, _ = split_ids(exercises); held = set(held)
    files = {name: [] for name in FILES}
    for meta, csv, bench in exercises:
        if bench:
            files["bench"] += exercise_rows(meta, csv, True)
        elif meta["id"] in held:
            files["heldout_exercises"] += exercise_rows(meta, csv, False)
            files["heldout_both"] += exercise_rows(meta, csv, False, "heldout", HELDOUT_WORDING_ROWS["heldout_both"], scripted=False)
        else:
            files["train"] += exercise_rows(meta, csv, False)
            files["heldout_wordings"] += exercise_rows(meta, csv, False, "heldout", HELDOUT_WORDING_ROWS["heldout_wordings"], scripted=False)
    n_test = 0
    for name in FILES:
        rows = files[name]
        random.Random(f"{ROW_SEED}:{name}").shuffle(rows)
        split, pre = {"train": ("train", "tr"), "bench": ("bench", "be")}.get(name, ("test", "te"))
        for n, r in enumerate(rows):
            if split == "test": n = n_test; n_test += 1                            # te_ ids are unique over the three held-out files
            r["id"] = f"{pre}_{WORKFLOW}_{n:06d}"; r["split"] = split
            f = json.loads(r["factors"]); f["file"] = name; r["factors"] = _dump(f)
    return tuple(files[name] for name in FILES)

# ---------------------------------------------------------------- statistics, README blocks
def stats(*files):
    """Counts per file: rows, exercises, distinct request wordings, the histogram of every question's gold label."""
    out = {}
    for name, rows in zip(FILES, files):
        hist = collections.defaultdict(collections.Counter)
        ex, wid = set(), set()
        for r in rows:
            f = json.loads(r["factors"]); ex.add(f["exercise"]); wid.add(f["wording_id"] or f"{f['kind']}.scripted")
            for q, g in json.loads(r["gold"]).items(): hist[q][g["label"]] += 1
        out[name] = {"rows": len(rows), "exercises": len(ex), "wordings": len(wid),
                     "hist": {q: dict(sorted(c.items())) for q, c in hist.items()}}
    return out

def counts_block(st):
    qs = list(questions_for([2, 3]))
    lines = [COUNTS_BEGIN, "", "| file | rows | exercises | request wordings (scripted ones counted once per kind) |", "|---|---|---|---|"]
    for name in FILES: lines.append(f"| {name}.jsonl | {st[name]['rows']} | {st[name]['exercises']} | {st[name]['wordings']} |")
    for q in qs:
        labels = sorted(set().union(*(st[n]["hist"][q] for n in FILES)))
        lines += ["", f"`{q}`", "", "| answer | " + " | ".join(FILES) + " |", "|---|" + "---|" * len(FILES)]
        lines += [f"| {l} | " + " | ".join(str(st[n]["hist"][q].get(l, 0)) for n in FILES) + " |" for l in labels]
    lines += ["", COUNTS_END]
    return "\n".join(lines)

def wordings_block():
    """Wordings per pool and per family, with the side of the split (README)."""
    lines = [WORDINGS_BEGIN, "", f"Wording split: seed {WORDING_SEED}, attempt {HALVES_ATTEMPT}.", "",
             "| pool | wordings | train side | held out |", "|---|---|---|---|"]
    for kind in KINDS + SLOT_KINDS:
        lines.append(f"| {kind} | {len(WORDINGS[kind])} | {len(HALVES[kind]['train'])} | {len(HALVES[kind]['heldout'])} |")
    tot = lambda h: sum(len(HALVES[k][h]) for k in HALVES)
    lines.append(f"| all | {len(WORDING_BY_ID)} | {tot('train')} | {tot('heldout')} |")
    lines += ["", "| family | wordings | train side | held out | pools |", "|---|---|---|---|---|"]
    held = half_ids("heldout")
    for fam in FAMILIES:
        ws = [x for x in WORDING_BY_ID.values() if x["family"] == fam]
        pools = sorted({x["id"].split(".")[0] for x in ws}, key=lambda k: (KINDS + SLOT_KINDS).index(k))
        lines.append(f"| {fam} | {len(ws)} | {sum(x['id'] not in held for x in ws)} | {sum(x['id'] in held for x in ws)} | {', '.join(pools)} |")
    lines += ["", "Held-out wording ids: " + ", ".join(sorted(held)) + ".", "", WORDINGS_END]
    return "\n".join(lines)

def update_readme(blocks, path=README):
    """Replaces each generated block (counts, wordings) of the README in place."""
    if not os.path.isfile(path): return False
    with open(path, encoding="utf-8") as f: text = f.read()
    for block in blocks:
        begin, end = block.split("\n", 1)[0], block.rsplit("\n", 1)[-1]
        if begin not in text: return False
        text = re.sub(re.escape(begin) + r".*?" + re.escape(end), lambda _: block, text, flags=re.S)
    with open(path, "w", encoding="utf-8", newline="\n") as f: f.write(text)
    return True

def write(rows, path):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=OUT); ap.add_argument("--no-readme", action="store_true")
    a = ap.parse_args()
    files = build()
    os.makedirs(a.out, exist_ok=True)
    for name, rows in zip(FILES, files): write(rows, os.path.join(a.out, f"{name}.jsonl"))
    st = stats(*files)
    if not a.no_readme: update_readme([counts_block(st), wordings_block()])
    print(json.dumps({k: {"rows": v["rows"], "exercises": v["exercises"], "wordings": v["wordings"]} for k, v in st.items()}))
