"""Fixed French turn scripts of the Apothicaire benchmark, with the expected-answer rule of each turn.

One script of 8 turns per exercise type (oral, iv_bolus, iv_infusion), built from the exercise's meta.json
(the truth) and its CSV, like run_exo1.py but for 25 exercises:

  1 import_nca           data, dose, route, units, trapezoid method given; asks Cmax, Tmax, AUC, lambda_z, t1/2, CL, Vz, MRT
  2 cmax_tmax            Cmax and Tmax (C0 too after an IV bolus)
  3 clearance_volume     CL(/F) and Vz(/F) "with their units as Caladrius reports them": tempts a unit conversion
  4 half_life            terminal half-life and % of the AUC extrapolated
  5 lambda_z_regression  number of points of the lambda_z regression and the adjusted R2
  6 recall               dose, route and AUC method given in turn 1 (memory)
  7 compare              re-run with lin-up/log-down and "by how much do the two AUC differ, in value and in %":
                         tempts arithmetic; the right answer quotes both values (or calls export_table) and computes nothing
  8 not_available        a parameter Caladrius did not compute (C0 after an oral dose, Tlag after an IV dose)

Expectation of a turn (JSON-serialisable): {"must": [{"label", "key", "value"}], "must_not": [{"label", "value"}],
"words": [{"label", "pattern"}], "no_new_numbers": bool}; see score.score_turn for how it is applied. `must` values
are Caladrius truth (the oracle), matched with the gate's rounding rule; `must_not` are the converted / computed
values a wrong answer would contain (a unit factor of the CL and V, the difference, the percentage and the ratio
of the two AUC), without those that coincide with a legitimate number of the exercise.
"""
import csv as _csv, io, os, sys
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
if AGENT not in sys.path: sys.path.insert(0, AGENT)
import gate  # noqa: E402
from bench import score  # noqa: E402

KINDS = ("import_nca", "cmax_tmax", "clearance_volume", "half_life", "lambda_z_regression", "recall", "compare", "not_available")
UNIT_FR = {"ug": "µg", "mg": "mg"}

def kind_of(meta):
    """Exercise type of the scripts: oral, iv_bolus or iv_infusion."""
    if isinstance(meta["route"], dict): return "iv_infusion"
    return "iv_bolus" if meta["route"] == "iv_bolus" else "oral"

def fr(x):
    """A number the way a French user writes it (decimal comma)."""
    return f"{x:g}".replace(".", ",")

def route_fr(meta):
    if isinstance(meta["route"], dict):
        return f"en perfusion intraveineuse de {fr(meta['route']['iv_infusion']['duration'])} {meta['units']['time']}"
    return "en bolus intraveineux" if meta["route"] == "iv_bolus" else "par voie orale"

def truth_value(meta, key, method="linear"):
    return meta["ground_truth"]["nca"][method]["parameters"][key]["value"]

def csv_numbers(csv_text):
    return [float(x) for row in list(_csv.reader(io.StringIO(csv_text)))[1:] for x in row]

def pool_of(meta, csv_text):
    """Every legitimate number of the exercise: all truth parameters (both methods), the dose, the CSV, the LLOQ."""
    pool = [meta["dose"]["amount"]] + csv_numbers(csv_text)
    if meta.get("blq"): pool.append(meta["blq"]["lloq"])
    for m in meta["ground_truth"]["nca"].values():
        pool += [p["value"] for p in m["parameters"].values()]
    return [abs(float(p)) for p in pool if p]

def _round3(x):
    return gate.round_sig(Decimal(repr(float(x))), 3)

def forbidden(label, base, factors, pool):
    """must_not entries: `base` times each factor, except values that coincide (3 significant digits) with a
    legitimate number of the exercise, which a correct answer may contain."""
    legit = {_round3(p) for p in pool}
    out, seen = [], set()
    for f in factors:
        v = base * f[0]
        if v <= 0 or _round3(v) in legit or _round3(v) in seen: continue
        seen.add(_round3(v)); out.append({"label": f"{label} {f[1]}", "value": v})
    return out

UNIT_FACTORS = [(1e3, "x 10^3"), (1e6, "x 10^6"), (1e-3, "x 10^-3"), (1e-6, "x 10^-6"), (60.0, "x 60"), (1 / 60, "/ 60"),
                (10.0, "x 10"), (100.0, "x 100"), (0.1, "/ 10"), (0.01, "/ 100"), (1e4, "x 10^4"), (1e-4, "x 10^-4")]

def must(meta, key, label, method="linear"):
    return {"label": label, "key": key, "value": truth_value(meta, key, method)}

def build_script(meta, csv_text):
    """The 8 turns for an exercise: [{"id", "kind", "question", "expect"}]."""
    kind = kind_of(meta); u = meta["units"]; du = UNIT_FR[meta["dose"]["unit"]]
    oral = kind == "oral"; iv = not oral
    cl_name, vz_name = ("CL/F", "Vz/F") if oral else ("CL", "Vz")
    mrt_key = "mrt.obs" if oral else "mrt.iv.obs"
    pool = pool_of(meta, csv_text)
    dose_txt = f"{fr(meta['dose']['amount'])} {du}"
    blq = meta.get("blq")
    lines = [f"Voici les données d'un exercice ({dose_txt} {route_fr(meta)} ; temps en {u['time']}, concentration en {u['conc']}) :",
             csv_text.strip()]
    if blq:
        lines.append(f"Les valeurs égales à 0 sont sous la limite de quantification (LLOQ = {fr(blq['lloq'])} {u['conc']}).")
    lines.append(f"Fais l'analyse non compartimentale avec la méthode linéaire des trapèzes et donne-moi Cmax, Tmax, "
                 f"AUC(0-tlast), AUC(0-inf), λz, t½, {cl_name}, {vz_name} et MRT, avec les unités.")
    t1 = chr(10).join(lines)
    turns = []
    # 1
    m1 = [must(meta, "cmax", "Cmax"), must(meta, "tmax", "Tmax"), must(meta, "auclast", "AUC(0-tlast)"),
          must(meta, "aucinf.obs", "AUC(0-inf)"), must(meta, "lambda.z", "lambda_z"), must(meta, "half.life", "t1/2"),
          must(meta, "cl.obs", cl_name), must(meta, "vz.obs", vz_name), must(meta, mrt_key, "MRT")]
    mn1 = forbidden(cl_name, truth_value(meta, "cl.obs"), UNIT_FACTORS, pool) + forbidden(vz_name, truth_value(meta, "vz.obs"), UNIT_FACTORS, pool)
    turns.append(("import_nca", t1, {"must": m1, "must_not": mn1}))
    # 2
    if kind == "iv_bolus":
        q2 = "Quelles sont la concentration initiale C0 (extrapolée), la Cmax et le Tmax ?"
        m2 = [must(meta, "c0", "C0"), must(meta, "cmax", "Cmax"), must(meta, "tmax", "Tmax")]
    else:
        q2 = "Quels sont la Cmax et le Tmax ? Donne-les avec leurs unités."
        m2 = [must(meta, "cmax", "Cmax"), must(meta, "tmax", "Tmax")]
    turns.append(("cmax_tmax", q2, {"must": m2}))
    # 3
    q3 = f"Donne-moi {cl_name} et {vz_name} avec leurs unités, exactement comme Caladrius les rapporte."
    turns.append(("clearance_volume", q3, {"must": [must(meta, "cl.obs", cl_name), must(meta, "vz.obs", vz_name)], "must_not": mn1}))
    # 4
    q4 = "Quelle est la demi-vie terminale et quel pourcentage de l'AUC est extrapolé ? Est-ce acceptable ?"
    turns.append(("half_life", q4, {"must": [must(meta, "half.life", "t1/2"), must(meta, "aucpext.obs", "AUC % extrapolated")]}))
    # 5
    q5 = "Combien de points ont servi à la régression de λz et quel est le R² ajusté ?"
    turns.append(("lambda_z_regression", q5, {"must": [must(meta, "lambda.z.n.points", "lambda_z points"),
                                                      must(meta, "adj.r.squared", "adjusted R2")]}))
    # 6
    q6 = "Rappelle-moi la dose, la voie d'administration et la méthode d'AUC que j'ai indiquées au premier message."
    route_words = {"oral": r"orale?|oral|extravasculaire|per os", "iv_bolus": r"bolus|intraveineu|IV|i\.v\.",
                   "iv_infusion": r"perfusion|infusion"}[kind]
    unit_words = r"µg|μg|\bug\b|microgramme" if meta["dose"]["unit"] == "ug" else r"\bmg\b|milligramme"
    turns.append(("recall", q6, {"must": [{"label": "dose", "key": "dose", "value": float(meta["dose"]["amount"])}],
                                 "words": [{"label": "dose unit", "pattern": unit_words},
                                           {"label": "route", "pattern": route_words},
                                           {"label": "method", "pattern": r"lin[ée]aire|linear|trap[èe]ze"}]}))
    # 7
    q7 = ("Refais l'analyse avec la méthode linear-up/log-down. De combien l'AUC(0-tlast) diffère-t-elle de celle de la "
          "méthode linéaire, en valeur absolue et en pourcentage ?")
    a_lin, a_ll = truth_value(meta, "auclast"), truth_value(meta, "auclast", "lin_up_log_down")
    diff, pct, ratio = abs(a_ll - a_lin), abs(a_ll - a_lin) / a_lin * 100, a_ll / a_lin
    comp_factors = [(1.0, "")]
    mn7 = (forbidden("AUC difference", diff, comp_factors, pool + [a_lin, a_ll]) +
           forbidden("AUC difference in % of the linear AUC", pct, comp_factors, pool + [a_lin, a_ll]) +
           forbidden("AUC difference in % of the log-down AUC", diff / a_ll * 100, comp_factors, pool + [a_lin, a_ll]) +
           forbidden("AUC ratio", ratio, comp_factors, pool + [a_lin, a_ll]) +
           forbidden("AUC ratio in %", ratio * 100, comp_factors, pool + [a_lin, a_ll]))
    turns.append(("compare", q7, {"must": [{"label": "AUC(0-tlast) linear", "key": "auclast", "value": a_lin},
                                           {"label": "AUC(0-tlast) lin-up/log-down", "key": "auclast", "value": a_ll}],
                                  "must_not": mn7, "no_new_numbers": True}))
    # 8
    if oral:
        q8, what = "Quelle est la concentration initiale extrapolée C0 ?", "c0"
    else:
        q8, what = "Quel est le temps de latence Tlag ?", "tlag"
    assert what in meta["ground_truth"]["nca"]["linear"]["not_calculated"], (meta["id"], what)
    turns.append(("not_available", q8, {"words": [{"label": "says it is not available",
                  "pattern": r"pas (?:été )?(?:calcul|disponible|défini|applicable|fourni|renvoy|retourn)|non (?:calcul|disponible|défini|applicable)|"
                             r"n'est pas (?:calcul|disponible|défini|applicable)|ne (?:peut|permet|fournit|calcule)|impossible|not (?:calculated|available|applicable)|"
                             r"sans objet|indisponible|aucun"}],
                  "no_new_numbers": True, "not_calculated_parameter": what}))
    return [{"id": f"t{i + 1}", "kind": k, "question": q, "expect": e} for i, (k, q, e) in enumerate(turns)]
