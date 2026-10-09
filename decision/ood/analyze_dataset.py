#!/usr/bin/env python
"""Part 2 attacks on the dataset and its baselines (no engine, no model).

  python decision/ood/analyze_dataset.py

Three questions:
  1. Does the generator's wording leak across the held-out split? The split is by exercise, but the WORDINGS pool of
     make_dataset.py is global, so the same request sentence should reappear in train. Measure it.
  2. Is "always answer the majority" the right baseline? Add a handful of deterministic rules built from the same
     generator regexes (dose unit, route) and from the question structure (auc_method, compare_pair, is_not_available).
  3. Do my own gold labels of decision/ood/requests.jsonl follow the project's stated conventions
     (decision/README.md "Our rows")? List the disagreements, because they decide how the OOD score is read.
Writes decision/ood/runs/analyze_dataset.json.
"""
import collections, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DECISION = os.path.dirname(HERE)
AGENT = os.path.dirname(DECISION)
for p in (AGENT, DECISION):
    if p not in sys.path: sys.path.insert(0, p)
from bench import scripts  # noqa: E402

DATA = os.path.join(DECISION, "data")
OUT = os.path.join(HERE, "runs")
UNIT_RE = re.compile(r"\d\s*(?:mg|µg|μg|ug)\b")
ROUTE_PAT = [(re.compile(r"perfusion", re.I), "iv_infusion"),
             (re.compile(r"bolus|injection intraveineuse rapide", re.I), "iv_bolus"),
             (re.compile(r"orale?\b|per os", re.I), "oral")]
FIT1 = re.compile(r"un compartiment|mono-?compartimental|1 compartiment|pk1|mono\b", re.I)
FIT2 = re.compile(r"deux compartiments|bicompartimental|2 compartiments|bi-?exponentiel|pk2", re.I)
SIM = re.compile(r"simul", re.I)
CMP = re.compile(r"compar|diff[ée]rence|[ée]cart|change|relance|refais le calcul", re.I)


def load(split):
    rows = []
    with open(os.path.join(DATA, split + ".jsonl"), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            rows.append({"id": r["id"], "state": json.loads(r["state"]), "gold": {q: g["label"] for q, g in json.loads(r["gold"]).items()},
                         "factors": json.loads(r["factors"])})
    return rows


def question_names(rows):
    return list(rows[0]["gold"])


def accuracy(rows, predict):
    """{question: (right, total)} for predict(row) -> {question: label}."""
    out = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        p = predict(r)
        for q, g in r["gold"].items():
            out[q][1] += 1
            out[q][0] += p.get(q) == g
    return {q: tuple(v) for q, v in out.items()}


def majority(train):
    c = collections.defaultdict(collections.Counter)
    for r in train:
        for q, g in r["gold"].items(): c[q][g] += 1
    return {q: v.most_common(1)[0][0] for q, v in c.items()}


def route_rule(row):
    s = row["state"]["user_dose_sentence"]
    for pat, lab in ROUTE_PAT:
        if pat.search(s): return lab
    return "unknown"


def analysis_rule(row):
    st, req = row["state"], row["state"]["request"]
    if not st["analyses"]: return "nca"
    if FIT2.search(req): return "fit_pk2"
    if FIT1.search(req): return "fit_pk1"
    if SIM.search(req): return "simulate"
    if CMP.search(req): return "compare"
    return "none_needed"


def auc_rule(row, base):
    a = base.get("analysis")
    if a == "nca": return "linear"
    if a == "compare": return "lin_up_log_down"
    return "not_applicable"


def na_rule(row, base):
    req = row["state"]["request"]
    route = base.get("route")
    if re.search(r"tlag|temps de latence|latence", req, re.I) and route in ("iv_bolus", "iv_infusion"): return "true"
    if re.search(r"\bc0\b|concentration initiale|extrapol[ée]e? à (?:l'instant )?z[ée]ro|à t\s*=\s*0", req, re.I) and route == "oral": return "true"
    return "false"


def pair_rule(row, base):
    ids = sorted(a["id"] for a in row["state"]["analyses"])
    if base.get("analysis") == "compare" and len(ids) >= 2: return f"{ids[0]}+{ids[1]}"
    return "not_applicable"


def as_questions(labels):
    """{question: label} with the gold keys of a row (asked_<k> etc.) from a {analysis, route, ...} dict."""
    out = {}
    for k, v in labels.items():
        if k == "asked":
            continue
        out[k] = v
    for k in ("cmax", "tmax", "c0", "auclast", "aucinf", "lambda_z", "half_life", "cl", "vz", "mrt", "aucpext",
              "lambda_z_points", "adj_r2", "tlag"):
        out[f"asked_{k}"] = "true" if k in labels.get("asked", []) else "false"
    return out


def my_requests():
    lines = []
    with open(os.path.join(HERE, "requests.jsonl"), encoding="utf-8") as f:
        for line in f:
            lines.append(json.loads(line))
    return lines


def main():
    os.makedirs(OUT, exist_ok=True)
    train, heldout, bench = load("train"), load("heldout"), load("bench")
    rep = {"rows": {"train": len(train), "heldout": len(heldout), "bench": len(bench)}}

    # 1. wording leakage
    tr_req = collections.Counter(r["state"]["request"] for r in train)
    tr_dose = collections.Counter(r["state"]["user_dose_sentence"] for r in train)
    tr_kind_req = collections.Counter((r["factors"]["kind"], r["state"]["request"]) for r in train)
    leak_req = round(sum(1 for r in heldout if r["state"]["request"] in tr_req) / len(heldout), 4)
    leak_dose = round(sum(1 for r in heldout if r["state"]["user_dose_sentence"] in tr_dose) / len(heldout), 4)
    leak_kind = round(sum(1 for r in heldout if (r["factors"]["kind"], r["state"]["request"]) in tr_kind_req) / len(heldout), 4)
    rep["leakage"] = {"heldout_rows": len(heldout), "distinct_requests_train": len(tr_req), "distinct_requests_heldout": len(set(r["state"]["request"] for r in heldout)),
                      "heldout_request_seen_in_train": leak_req, "heldout_dose_sentence_seen_in_train": leak_dose,
                      "heldout_(kind,request)_seen_in_train": leak_kind,
                      "bench_request_seen_in_train": round(sum(1 for r in bench if r["state"]["request"] in tr_req) / len(bench), 4)}
    # distinct requests in heldout not in train
    rep["leakage"]["heldout_requests_absent_from_train"] = sorted({r["state"]["request"] for r in heldout if r["state"]["request"] not in tr_req})[:20]

    # 2. baselines on heldout
    maj = majority(train)
    qs = question_names(train)
    base_rows = {}
    for q in qs:
        base_rows[q] = {"majority": (sum(1 for r in heldout if r["gold"][q] == maj[q]), len(heldout))}
    def rule_predict(row):
        b = {"analysis": analysis_rule(row), "route": route_rule(row),
             "dose_has_unit": "true" if UNIT_RE.search(row["state"]["user_dose_sentence"]) else "false"}
        b["auc_method"] = auc_rule(row, b); b["is_not_available"] = na_rule(row, b); b["compare_pair"] = pair_rule(row, b)
        return b
    rp = [rule_predict(r) for r in heldout]
    for i, r in enumerate(heldout):
        r["_rule"] = rp[i]
    rules = accuracy(heldout, lambda r: r["_rule"])
    rep["heldout_baselines"] = {}
    for q in qs:
        if q.startswith("asked_"):
            continue
        m = base_rows[q]["majority"][0] / base_rows[q]["majority"][1]
        rr = rules.get(q, (0, 0))
        rep["heldout_baselines"][q] = {"majority": round(m, 4), "rule": round(rr[0] / rr[1], 4) if rr[1] else None}
    # a rule for asked_<k> would need a wording table; report the majority there only
    rep["heldout_baselines"]["asked_*_mean_majority"] = round(
        sum(base_rows[q]["majority"][0] / base_rows[q]["majority"][1] for q in qs if q.startswith("asked_")) / 14, 4)

    # overall majority and overall rule over the 5 non-asked + 14 asked questions
    n = len(heldout)
    tot_maj = sum(base_rows[q]["majority"][0] for q in qs) / (n * len(qs))
    tot_rule = (sum(rules[q][0] for q in qs if not q.startswith("asked_")) + sum(base_rows[q]["majority"][0] for q in qs if q.startswith("asked_"))) / (n * len(qs))
    rep["heldout_overall"] = {"majority_20q": round(tot_maj, 4), "rule_plus_majority_asked": round(tot_rule, 4)}

    # 3. my gold vs the project conventions
    lines = my_requests()
    auc_mismatch, na_extra, route_note = [], [], []
    for l in lines:
        g = l["gold"]
        # project convention: auc_method = linear on the first NCA, lin_up_log_down on compare, not_applicable otherwise
        proj = "linear" if (g["analysis"] == "nca" and not l["prior_analyses"]) else ("lin_up_log_down" if g["analysis"] == "compare" else "not_applicable")
        if proj != g["auc_method"]:
            auc_mismatch.append({"id": l["id"], "mine": g["auc_method"], "project_convention": proj, "analysis": g["analysis"], "tags": l["tags"]})
        # project has no label for out-of-scope / out-of-schema; the harness regexes only know mg/ug
        if g["is_not_available"] and l["tags"] and any(t in l["tags"] for t in ("out-of-scope", "parameter-not-in-schema", "population", "steady-state", "urine", "bioequivalence")):
            na_extra.append({"id": l["id"], "tags": l["tags"]})
        if g["route"] == "unknown":
            route_note.append(l["id"])
    rep["my_gold_vs_project_conventions"] = {
        "requests": len(lines),
        "auc_method_disagreements": len(auc_mismatch), "auc_method_disagreement_ids": auc_mismatch,
        "is_not_available_true_but_outside_the_project_label_space": na_extra,
        "route_unknown_lines": route_note,
        "dose_has_unit_false_lines": [l["id"] for l in lines if not l["gold"]["dose_has_unit"]],
    }
    with open(os.path.join(OUT, "analyze_dataset.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    print(json.dumps(rep, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
