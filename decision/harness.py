#!/usr/bin/env python
"""Deterministic harness of the decision path (D-01, step 4): the decision model decides, the harness acts and renders.

One `Harness` holds one Caladrius MCP session (the client of apothicaire.py, imported) for one conversation. Per user turn it

  (a) builds the state exactly as decision/make_dataset.py does (`make_dataset.make_state`, `make_dataset.split_first_message`)
      and the closed question set (`make_dataset.questions_for`);
  (b) asks the injected decision model, `decide(state, questions) -> {question: label}` (a label string, or a dict with "label",
      or a bool for a noul question);
  (c) acts on the closed answers: `data_import` once per conversation, `nca_run` with the decided route, the dose of the user's
      sentence and the decided AUC method, `analysis_get` to read the parameter asked (or the settings, for a recall),
      `analysis_compare` on the decided pair, a stated refusal for `is_not_available`, nothing else for `none_needed`;
  (d) renders a French answer from fixed templates. Every number of an answer is an engine value as the digest of apothicaire.py
      shows it ("value unit", 6 significant digits, the unit labelled from the worksheet), or a number the user wrote (the dose of
      the recall). The harness computes nothing: no arithmetic on engine values, no unit conversion, no language model.

What the harness reads from the user's text itself, deterministically (not a decision): the dose amount and its unit token (the
number right before mg / µg / ug), the infusion duration (the number after "perfusion", with its time unit), the column names and
units of the CSV header. A missing route, dose, dose unit or infusion duration is asked for, never guessed; an infusion duration in
another time unit than the data is asked again in the data's unit (no conversion).

Conventions:
  * the reference analysis of a reading turn is the analysis of the decided AUC method when there is one, else the first NCA of the
    project (the one run with the user's settings);
  * a compare whose AUC method has no analysis yet re-runs the reference analysis with that method (same dose, same route), then asks
    the decision model again on the new state: the dataset describes the compare turn after the re-run (decision/README.md), so the
    pair to compare is decided on that state;
  * the parameters shown are the ones whose `asked_<key>` answer is true, in the engine's order, nothing else: an NCA turn where no
    `asked_*` is true runs the analysis, prints no value and says that no parameter was designated; a reading turn where none is true
    is a recall of the settings (dose, route, AUC method);
  * `is_not_available` = true is checked against the engine: when Caladrius did compute the parameter, its value is given and the
    turn records the conflict (a false refusal would be a wrong answer).
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
for p in (AGENT, HERE):
    if p not in sys.path: sys.path.insert(0, p)
import apothicaire  # noqa: E402
from numtext import value_text  # noqa: E402,F401  (shared with the digest of apothicaire.py)
import make_dataset as md  # noqa: E402

METHODS = ("linear", "lin_up_log_down")
ENGINE_ROUTE = {"oral": "extravascular", "iv_bolus": "iv_bolus", "iv_infusion": "iv_infusion"}
# parameter key (asked_<key>) -> engine (PKNCA) key; mrt depends on the route (see engine_key)
ENGINE_KEY = {"cmax": "cmax", "tmax": "tmax", "c0": "c0", "auclast": "auclast", "aucinf": "aucinf.obs", "lambda_z": "lambda.z",
              "half_life": "half.life", "cl": "cl.obs", "vz": "vz.obs", "aucpext": "aucpext.obs",
              "lambda_z_points": "lambda.z.n.points", "adj_r2": "adj.r.squared", "tlag": "tlag"}
METHOD_FR = {"linear": "trapèzes linéaires (linear)", "lin_up_log_down": "linear-up/log-down", "lin_log": "lin-log"}
METHOD_SHORT_FR = {"linear": "linéaire", "lin_up_log_down": "linear-up/log-down", "lin_log": "lin-log"}
ANALYSIS_FR = {"fit_pk1": "ajustement d'un modèle à un compartiment", "fit_pk2": "ajustement d'un modèle à deux compartiments",
               "simulate": "simulation à partir d'un modèle ajusté"}

# ---------------------------------------------------------------- templates (French; no number is ever written in them)
T_NO_DATA = ("Je n'ai pas encore de données : collez le tableau concentration-temps (une ligne d'en-tête avec les unités, puis les "
             "mesures), avec la dose, la voie d'administration et la question.")
T_ASK_ROUTE = ("Je ne lance pas l'analyse : la voie d'administration n'est pas indiquée. Précisez-la (bolus intraveineux, perfusion "
               "intraveineuse avec sa durée, ou voie orale).")
T_ASK_DOSE_UNIT = "Je ne lance pas l'analyse : la dose n'a pas d'unité. Précisez-la (mg, µg...)."
T_ASK_DOSE = "Je ne lance pas l'analyse : je ne trouve pas la dose dans votre message. Indiquez-la avec son unité (mg, µg...)."
T_ASK_DURATION = ("Je ne lance pas l'analyse : la durée de la perfusion n'est pas indiquée. Précisez-la, dans l'unité de temps des "
                  "données ({t}).")
T_ASK_DURATION_UNIT = ("Je ne lance pas l'analyse : la durée de la perfusion est donnée en {u} et les temps des données en {t}. "
                       "Donnez la durée en {t} (je ne convertis pas les unités).")
T_NO_ANALYSIS = ("Aucune analyse n'est encore faite dans ce projet : demandez d'abord une analyse non compartimentale (avec la dose, "
                 "la voie et la méthode d'AUC).")
T_NOT_WIRED = ("Cette demande ({what}) n'est pas encore prise en charge par le harnais de décision : seules l'analyse non "
               "compartimentale, la lecture de ses résultats et la comparaison de deux analyses le sont.")
T_NO_PARAMETER = ("L'analyse non compartimentale est faite, mais votre demande ne désigne aucun paramètre à afficher : "
                  "je ne donne aucune valeur. Indiquez le ou les paramètres voulus (Cmax, Tmax, AUC, λz, t½, CL, Vz, MRT...).")
T_UNDECIDED = "Je n'ai pas pu interpréter la demande ({qs}). Pouvez-vous la reformuler ?"
T_TOOL_FAILED = "Caladrius a refusé l'appel {tool} : « {error} ». Je ne donne aucune valeur."
T_WHICH_PAIR = "Quelles analyses faut-il comparer ? Analyses du projet : {analyses}."
T_NOT_AVAILABLE = "{label} n'est pas calculé par Caladrius pour cette voie d'administration : {route}."
T_NOT_AVAILABLE_REASON = " Raison donnée par Caladrius : « {reason} »."
T_NOT_AVAILABLE_NO_ANALYSIS = "{label} n'est pas calculé par Caladrius pour cette voie d'administration ; aucune analyse n'est encore faite."

# ---------------------------------------------------------------- reading the user's text (no arithmetic)
_NUM = r"(\d+(?:[.,]\d+)?)"
_DOSE_RE = re.compile(_NUM + r"\s*(mg|µg|μg|ug)(?![\w/])", re.I)
_DURATION_RE = re.compile(r"perfusion\D{0,40}?" + _NUM + r"\s*(h|min|j|jours?|heures?)\b", re.I)
_HEADER_CELL_RE = re.compile(r"^\s*(.*?)\s*\(([^()]*)\)\s*$")

def parse_number(text):
    """A number as the user wrote it (decimal comma or point): int when it has no decimal part, else float."""
    t = text.replace(",", ".")
    return float(t) if "." in t else int(t)

def parse_dose(sentence):
    """(amount, unit token as written) of the first number followed by a mass unit, or (None, None)."""
    m = _DOSE_RE.search(sentence or "")
    return (parse_number(m.group(1)), m.group(2)) if m else (None, None)

def parse_duration(sentence):
    """(duration, time unit as written) of an infusion ("perfusion ... de 2 h"), or (None, None)."""
    m = _DURATION_RE.search(sentence or "")
    return (parse_number(m.group(1)), m.group(2)) if m else (None, None)

def header_columns(csv_text):
    """data_import columns from a header "time (h),conc (ng/mL)": [{"name", "unit"}]; a cell without a unit gives its name only."""
    out = []
    for cell in csv_text.strip().splitlines()[0].split(","):
        m = _HEADER_CELL_RE.match(cell)
        out.append({"name": m.group(1), "unit": m.group(2).strip()} if m else {"name": cell.strip()})
    return out

# ---------------------------------------------------------------- the decision model's answers
def normalize_answers(raw, questions):
    """({question: label or None}, [questions whose answer is outside the offered options]). A label may come as a string, a dict
    with "label" (the typed-decisions gold format) or a bool (noul)."""
    out, outside = {}, []
    raw = raw if isinstance(raw, dict) else {}
    for q, spec in questions.items():
        v = raw.get(q)
        if isinstance(v, dict): v = v.get("label")
        if isinstance(v, bool): v = "true" if v else "false"
        v = None if v is None else str(v)
        opts = set(spec["criteria"]) if spec["type"] == "choice" else {"false", "true"}
        if v not in opts: outside.append(q); v = None
        out[q] = v
    return out, outside

# ---------------------------------------------------------------- rendering (pure functions of engine digests)
def engine_key(param, route):
    """Engine key of a parameter asked (key of make_dataset.PARAMETERS); MRT is mrt.obs after an extravascular dose, mrt.iv.obs otherwise."""
    if param == "mrt": return "mrt.obs" if route == "extravascular" else "mrt.iv.obs"
    return ENGINE_KEY.get(param)

def label_fr(param, route):
    """French label of a parameter; its first words are the labels the oracle of bench/score.py reads (CL/F and Vz/F after an oral dose)."""
    f = "/F" if route == "extravascular" else ""
    return {"cmax": "Cmax", "tmax": "Tmax", "c0": "C0 (concentration initiale extrapolée)", "auclast": "AUC(0-tlast)",
            "aucinf": "AUC(0-inf)", "aucpext": "AUC extrapolée (%)", "lambda_z": "λz (constante d'élimination terminale)",
            "lambda_z_points": "Nombre de points de la régression terminale", "adj_r2": "R² ajusté de la régression terminale",
            "half_life": "t½ (demi-vie terminale)", "cl": f"CL{f} (clairance)", "vz": f"Vz{f} (volume de distribution)",
            "mrt": "MRT (temps moyen de résidence)", "tlag": "Tlag (temps de latence)"}.get(param, param)

def route_fr(route, time_unit=None, with_duration=True):
    if route == "extravascular": return "voie orale (extravasculaire)"
    if route == "iv_bolus": return "bolus intraveineux"
    if isinstance(route, dict) and "iv_infusion" in route:
        d = (route["iv_infusion"] or {}).get("duration")
        if with_duration and d is not None: return f"perfusion intraveineuse de {value_text(d)} {time_unit or '(unité de temps des données)'}"
        return "perfusion intraveineuse"
    return f"{route}"

def _subject_blocks(digest):
    subs = digest.get("subjects") or []
    return [(s, (f"Sujet {s.get('subject')} :" if len(subs) > 1 else None)) for s in subs]

def _not_calculated_reason(subject, key):
    for msg, names in (subject.get("not_calculated_messages") or {}).items():
        if key in names: return msg
    for code, names in (subject.get("not_calculated") or {}).items():
        if key in names: return code
    return None

def _warnings(digest, subject):
    out = [f"Avertissement de Caladrius : « {w.get('message', w)} »." for w in (digest.get("unit_warnings") or [])]
    out += [f"Alerte qualité de Caladrius : « {m} »." for m in (subject.get("flag_messages") or [])]
    return out

def render_header(digest, time_unit=None):
    """First line of a reading: which analysis, method, dose and route the values come from (all from the engine)."""
    s = (digest.get("subjects") or [{}])[0]
    method = (digest.get("options_used") or {}).get("auc_method")
    dose = s.get("dose")
    return (f"Résultats de Caladrius (analyse {digest.get('analysis')}, méthode d'AUC {METHOD_FR.get(method, method)}, "
            f"dose {value_text(dose) if dose is not None else 'non indiquée'}, {route_fr(s.get('route'), time_unit)}) :")

def render_params(digest, params, time_unit=None, footer=True):
    """Lines "- label : value unit" for the parameters asked (keys of make_dataset.PARAMETERS), per subject, in the order of the engine's
    parameters; a parameter Caladrius did not compute is listed with the engine's reason. footer=False writes the not-computed ones
    inline instead of at the end."""
    lines = [render_header(digest, time_unit)]
    for s, head in _subject_blocks(digest):
        if head: lines.append(head)
        if "parameters" not in s:
            lines.append(f"Caladrius n'a pas pu analyser ce sujet : « {json.dumps(s.get('outcome'), ensure_ascii=False)} ».")
            continue
        route, vals, missing, found = s.get("route"), s["parameters"], [], []
        order = {k: i for i, k in enumerate(vals)}
        for p in params:
            k = engine_key(p, route)
            if k in vals: found.append((order[k], p, k))
            else: missing.append((p, _not_calculated_reason(s, k)))
        lines += [f"- {label_fr(p, route)} : {value_text(vals[k])}" for _, p, k in sorted(found)]            # the engine's order
        for p, why in missing:
            text = f"{label_fr(p, route)} n'est pas calculé par Caladrius" + (f" (« {why} »)" if why else "") + "."
            lines.append(("- " + text) if not footer else text)
        lines += _warnings(digest, s)
    return "\n".join(lines)

def render_recall(digest, dose_unit=None, time_unit=None):
    """The settings of an analysis as Caladrius recorded them; the dose unit is the token of the user's sentence (Caladrius never
    receives the dose unit on this path)."""
    s = (digest.get("subjects") or [{}])[0]
    method = (digest.get("options_used") or {}).get("auc_method")
    dose = value_text(s.get("dose")) if s.get("dose") is not None else "non indiquée"
    unit = (f" {dose_unit} (unité de votre premier message ; Caladrius a reçu la dose sans unité)" if dose_unit
            else " (sans unité : vous n'en avez pas indiqué)")
    return "\n".join([f"Réglages de l'analyse {digest.get('analysis')} tels que Caladrius les a enregistrés :",
                      f"- Dose : {dose}{unit}",
                      f"- Voie d'administration : {route_fr(s.get('route'), time_unit)}",
                      f"- Méthode d'AUC : {METHOD_FR.get(method, method)}"])

def compare_parts(row):
    """A row of the analysis_compare digest ("a 14.6515 h*mg/L | b 14.3537 h*mg/L | difference ... | percent ... | ratio ...") as
    {"a": "14.6515 h*mg/L", ...}: the shown text split at its separators, nothing parsed as a number."""
    out = {}
    for part in row.split(" | "):
        if part.startswith("not comparable: "): out["not_comparable"] = part[len("not comparable: "):]; continue
        k, _, rest = part.partition(" ")
        out[k] = value_text(rest)
    return out

def render_compare(cdigest, method_a, method_b, route=None):
    """The analysis_compare result (b minus a, computed by Caladrius). method_a / method_b: the AUC methods of the two analyses."""
    ia, ib = (cdigest.get("a") or {}).get("analysis"), (cdigest.get("b") or {}).get("analysis")
    ma, mb = METHOD_SHORT_FR.get(method_a, method_a), METHOD_SHORT_FR.get(method_b, method_b)
    lines = [f"Comparaison calculée par Caladrius entre l'analyse {ia} et l'analyse {ib} (b - a) :"]
    inv = {v: k for k, v in ENGINE_KEY.items()}; inv.update({"mrt.obs": "mrt", "mrt.iv.obs": "mrt"})
    rows = cdigest.get("parameters") or {}
    for name, row in rows.items():
        p, lab = compare_parts(row), label_fr(inv.get(name, name), route)
        if len(rows) == 1:
            lines += [f"- {lab}, méthode {ma} (analyse {ia}) : {p.get('a', 'aucune valeur')}",
                      f"- {lab}, méthode {mb} (analyse {ib}) : {p.get('b', 'aucune valeur')}"]
            if "difference" in p: lines.append(f"- Différence (b - a) : {p['difference']}")
            if "percent" in p: lines.append(f"- Différence relative : {p['percent']}")
            if "ratio" in p: lines.append(f"- Rapport b/a : {p['ratio']}")
            if "not_comparable" in p: lines.append(f"- Non comparable : « {p['not_comparable']} »")
        else:
            bits = [f"analyse {ia} {p.get('a', 'aucune valeur')}", f"analyse {ib} {p.get('b', 'aucune valeur')}"]
            bits += [f"{fr} {p[k]}" for k, fr in (("difference", "différence"), ("percent", "différence relative"), ("ratio", "rapport b/a")) if k in p]
            lines.append(f"- {lab} : " + " ; ".join(bits))
    for why, names in (cdigest.get("not_comparable") or {}).items():
        lines.append(f"Non comparables (« {why} ») : {', '.join(names)}.")
    if not rows and not cdigest.get("not_comparable"): lines.append("Caladrius ne renvoie aucun paramètre commun.")
    return "\n".join(lines)

def render_refusal(param, digest=None, route=None):
    """The stated refusal of a parameter Caladrius does not compute for the route, with the engine's reason when an analysis exists."""
    lab = label_fr(param, route) if param in ENGINE_KEY or param == "mrt" else "Ce paramètre"
    if digest is None: return T_NOT_AVAILABLE_NO_ANALYSIS.format(label=lab)
    s = (digest.get("subjects") or [{}])[0]
    text = T_NOT_AVAILABLE.format(label=lab, route=route_fr(s.get("route"), with_duration=False))
    why = _not_calculated_reason(s, engine_key(param, s.get("route"))) if param in ENGINE_KEY or param == "mrt" else None
    return text + (T_NOT_AVAILABLE_REASON.format(reason=why) if why else "")

# ---------------------------------------------------------------- the harness
class Harness:
    """One conversation: one MCP session, the project's analyses, the tool log. `decide(state, questions)` is the decision model."""
    def __init__(self, decide, mcp=None, mcp_bin=None):
        self.decide = decide
        self.mcp = mcp if mcp is not None else apothicaire.MCPClient([mcp_bin or apothicaire.MCP_BIN])
        self.units = {}            # worksheet id -> units reported by Caladrius (filled by apothicaire.render_tool_result)
        self.tool_log = []         # every MCP call: turn, name, args, ok, text, shown (the digest)
        self.user_texts = []
        self.data = None           # {"intro", "csv", "notes"} of the first message that carried data
        self.worksheet = None
        self.analyses = []         # [{"id", "kind", "auc_method", "args"}] in creation order
        self.turns = 0
        self._info = None

    def close(self): self.mcp.close()

    # -- engine calls
    def _call(self, name, args):
        """One MCP call, logged; returns the digest (dict) or None when the call failed (the error text is in the log)."""
        try: ok, text = self.mcp.call(name, args)
        except apothicaire.MCPError as e: ok, text = False, f"mcp error: {e}"
        shown = apothicaire.render_tool_result(name, ok, text, self.units)
        self.tool_log.append({"turn": self.turns, "name": name, "args": args, "ok": ok, "text": text, "shown": shown})
        if not ok: return None
        try: return json.loads(shown)
        except ValueError: return None

    def _failed(self, name):
        last = self.tool_log[-1]
        return T_TOOL_FAILED.format(tool=name, error=last["text"].strip()[:300])

    def _time_unit(self):
        return (self.units.get(self.worksheet) or {}).get("time")

    def _import(self):
        if self.worksheet is None:
            d = self._call("data_import", {"name": "donnees", "csv": self.data["csv"], "columns": header_columns(self.data["csv"])})
            if d is not None: self.worksheet = (d.get("worksheet") or {}).get("id")
        return self.worksheet

    def _run_nca(self, dose, route, method):
        args = {"worksheet": self.worksheet, "dose": dose, "route": route}
        if method: args["options"] = {"auc_method": method}
        d = self._call("nca_run", args)
        if d is None: return None
        self.analyses.append({"id": d.get("analysis"), "kind": "nca", "auc_method": (d.get("options_used") or {}).get("auc_method"), "args": args})
        return d

    def _reference(self, method):
        same = [a for a in self.analyses if a["auc_method"] == method]
        return same[0] if same else (self.analyses[0] if self.analyses else None)

    # -- decisions
    @staticmethod
    def asked(a):
        """The parameters asked: the keys of make_dataset.PARAMETERS whose `asked_<key>` answer is true."""
        return [k for k in md.PARAMETERS if a.get(f"asked_{k}") == "true"]

    def _ask(self, request):
        state = md.make_state(self.data["csv"], self.data["intro"], list(self.data["notes"]), request,
                              [{"id": a["id"], "kind": a["kind"], "auc_method": a["auc_method"]} for a in self.analyses])
        questions = md.questions_for(sorted(a["id"] for a in self.analyses))
        answers, outside = normalize_answers(self.decide(state, questions), questions)
        self._info["decisions"].append({"state": state, "answers": answers, "outside_options": outside})
        return answers

    def turn(self, text):
        """One user message -> (answer, info). info: {"decisions": [{"state", "answers", "outside_options"}], "notes": [...]}."""
        self.turns += 1; self.user_texts.append(text)
        self._info = {"decisions": [], "notes": []}
        if self.data is None:
            first = md.split_first_message(text)
            if not first["csv"]: return T_NO_DATA, self._info
            self.data = {"intro": first["intro"], "csv": first["csv"], "notes": first["notes"]}
            request = first["request"]
        else:
            request = text.strip()
        a = self._ask(request)
        return self._act(a, request), self._info

    def _act(self, a, request):
        if a["is_not_available"] == "true": return self._refuse(a)
        kind = a["analysis"]
        if kind == "nca": return self._nca(a)
        if kind == "compare": return self._compare(a, request)
        if kind in ANALYSIS_FR: return T_NOT_WIRED.format(what=ANALYSIS_FR[kind])
        if kind == "none_needed": return self._read(a)
        return T_UNDECIDED.format(qs="type d'analyse")

    # -- actions
    def _nca(self, a):
        intro = self.data["intro"]
        if a["route"] in (None, "unknown"): return T_ASK_ROUTE
        if a["dose_has_unit"] != "true": return T_ASK_DOSE_UNIT
        dose, _ = parse_dose(intro)
        if dose is None: return T_ASK_DOSE
        route = ENGINE_ROUTE[a["route"]]
        cols = header_columns(self.data["csv"])
        data_time = cols[0].get("unit") if cols else None
        if route == "iv_infusion":
            dur, dur_unit = parse_duration(intro)
            if dur is None: return T_ASK_DURATION.format(t=data_time or "l'unité des données")
            if data_time and dur_unit != data_time: return T_ASK_DURATION_UNIT.format(u=dur_unit, t=data_time)
            route = {"iv_infusion": {"duration": dur}}
        if self._import() is None: return self._failed("data_import")
        method = a["auc_method"] if a["auc_method"] in METHODS else None
        d = self._run_nca(dose, route, method)
        if d is None: return self._failed("nca_run")
        ps = self.asked(a)
        if not ps: return T_NO_PARAMETER
        return render_params(d, ps, self._time_unit())

    def _read(self, a):
        ref = self._reference(a["auc_method"])
        if ref is None: return T_NO_ANALYSIS
        d = self._call("analysis_get", {"analysis": ref["id"]})
        if d is None: return self._failed("analysis_get")
        ps = self.asked(a)
        if not ps: return render_recall(d, parse_dose(self.data["intro"])[1], self._time_unit())
        return render_params(d, ps, self._time_unit())

    def _refuse(self, a):
        p = next(iter(self.asked(a)), None)          # the first parameter asked; a refusal names one
        ref = self._reference(a["auc_method"])
        if ref is None: return render_refusal(p)
        d = self._call("analysis_get", {"analysis": ref["id"]})
        if d is None: return self._failed("analysis_get")
        s = (d.get("subjects") or [{}])[0]
        k = engine_key(p, s.get("route")) if p else None
        if k and k in (s.get("parameters") or {}):          # the engine did compute it: its value, not a false refusal
            self._info["notes"].append(f"is_not_available overruled: Caladrius computed {k}")
            return render_params(d, [p], self._time_unit())
        return render_refusal(p, d, s.get("route"))

    def _compare(self, a, request):
        if not self.analyses: return T_NO_ANALYSIS
        m = a["auc_method"]
        if m in METHODS and not any(x["auc_method"] == m for x in self.analyses):
            ref = self.analyses[0]
            if self._run_nca(ref["args"]["dose"], ref["args"]["route"], m) is None: return self._failed("nca_run")
            a = self._ask(request)                            # decided again on the state after the re-run
        pair = a["compare_pair"]
        if not pair or "+" not in pair:
            lst = ", ".join(f"analyse {x['id']} (NCA, {METHOD_SHORT_FR.get(x['auc_method'], x['auc_method'])})" for x in self.analyses)
            return T_WHICH_PAIR.format(analyses=lst)
        ia, ib = (int(x) for x in pair.split("+"))
        by_id = {x["id"]: x for x in self.analyses}
        route = (by_id.get(ia) or {}).get("args", {}).get("route")
        args = {"a": ia, "b": ib}
        keys = [engine_key(p, route) for p in self.asked(a)]
        if keys: args["parameters"] = keys
        d = self._call("analysis_compare", args)
        if d is None: return self._failed("analysis_compare")
        return render_compare(d, (by_id.get(ia) or {}).get("auc_method"), (by_id.get(ib) or {}).get("auc_method"), route)
