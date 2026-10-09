"""The reviewer's deterministic rules (decision/ood/analyze_dataset.py) as a decider for decision/eval_ood.py.

  PYTHONPATH=decision/ood python decision/eval_ood.py --decider rules_decider:decide --no-run

Route, analysis, auc_method, dose_has_unit, is_not_available and compare_pair come from the reviewer's regexes; every asked_<key> is the
majority answer (false), because the reviewer wrote no wording table for them.
"""
import analyze_dataset as A

def decide(state, questions):
    row = {"state": state}
    b = {"analysis": A.analysis_rule(row), "route": A.route_rule(row),
         "dose_has_unit": "true" if A.UNIT_RE.search(state["user_dose_sentence"]) else "false"}
    b["auc_method"] = A.auc_rule(row, b); b["is_not_available"] = A.na_rule(row, b); b["compare_pair"] = A.pair_rule(row, b)
    return {q: b.get(q, "false") for q in questions}

decide.name = "rules-reviewer"
