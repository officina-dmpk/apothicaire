#!/usr/bin/env python
"""Regenerates tests/golden/*.json from the Caladrius MCP server. Run by hand, never by the tests.

Only PUBLIC data is used (caladrius/oracle/data/theoph.csv, indometh.csv, edge_*.csv). Each golden
file stores the exact tool arguments, the answers of data_import and nca_run as the server sent
them (parsed JSON, nothing edited), and the tools/list answer is stored once in tools_list.json.

  python tests/make_golden.py            (needs the server built: see agent/README.md)
"""
import csv, io, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
sys.path.insert(0, AGENT)
import apothicaire  # noqa: E402

DATA = os.path.join(AGENT, "..", "caladrius", "oracle", "data")
OUT = os.path.join(HERE, "golden")
UNITS = [{"name": "time", "unit": "h"}, {"name": "conc", "unit": "mg/L"}]
UNITS_DOSE = UNITS + [{"name": "dose", "unit": "mg"}]

def subset(filename, subjects=None, drop=()):
    with open(os.path.join(DATA, filename), encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if subjects is not None: rows = [r for r in rows if r["subject"] in subjects]
    names = [k for k in rows[0] if k not in drop]
    out = io.StringIO(); w = csv.writer(out, lineterminator="\n"); w.writerow(names)
    for r in rows: w.writerow([r[k] for k in names])
    return out.getvalue()

# name -> (source description, data_import args, nca_run args without the worksheet id)
CASES = {
    "theoph_s1_oral_dose_arg": (
        "theoph.csv, subject 1, dose column dropped: the dose is an argument of nca_run",
        {"name": "theoph_s1", "csv": subset("theoph.csv", {"1"}, drop=("dose",)), "columns": UNITS},
        {"dose": 319.992, "route": "extravascular", "options": {"auc_method": "linear"}}),
    "indometh_s1_iv_bolus": (
        "indometh.csv, subject 1, dose column (25 mg, a test constant of the oracle data)",
        {"name": "indometh_s1", "csv": subset("indometh.csv", {"1"}), "columns": UNITS_DOSE},
        {"route": "iv_bolus", "options": {"auc_method": "lin_up_log_down"}}),
    "edge_blq_6_subjects": (
        "edge_blq.csv, 6 subjects: BLQ points removed from lambda_z, short span and high extrapolation flags",
        {"name": "edge_blq", "csv": subset("edge_blq.csv"), "columns": UNITS_DOSE},
        {"route": "extravascular", "options": {"auc_method": "linear"}}),
    "edge_iv_extravascular_no_rise": (
        "edge_iv.csv, 3 subjects, analysed as extravascular: a not-calculated reason beyond the route",
        {"name": "edge_iv", "csv": subset("edge_iv.csv"), "columns": UNITS_DOSE},
        {"route": "extravascular", "options": {"auc_method": "linear"}}),
    "edge_negative_subject_errors": (
        "edge_negative.csv, 2 subjects: each subject's outcome is an error (negative concentration)",
        {"name": "edge_negative", "csv": subset("edge_negative.csv"), "columns": UNITS_DOSE},
        {"route": "extravascular", "options": {"auc_method": "linear"}}),
}

def engine_commit():
    repo = os.path.join(AGENT, "..", "caladrius")
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain", "--", "crates", "apps"], cwd=repo, text=True).strip())
        return head + ("+uncommitted changes in crates/apps" if dirty else "")
    except Exception: return "unknown"

COMPARE_CASE = ("theoph_s1_compare_linear_vs_lin_up_log_down",
                "theoph.csv, subject 1 (dose argument): the same worksheet analysed with the linear and the lin-up/log-down AUC, then analysis_compare(a, b)")

def make_compare(commit):
    """tests/golden/compare/<case>.json: data_import, two nca_run, analysis_compare (all on one server session)."""
    name, source = COMPARE_CASE
    _, imp, nca = CASES["theoph_s1_oral_dose_arg"]
    c = apothicaire.MCPClient([apothicaire.MCP_BIN])
    try:
        ok, text = c.call("data_import", imp); assert ok, text
        ws = json.loads(text); wid = ws["worksheet"]["id"]
        calls, results = [{"tool": "data_import", "arguments": imp}], {"data_import_result": ws}
        ids = []
        for method in ("linear", "lin_up_log_down"):
            args = {"worksheet": wid, **nca, "options": {"auc_method": method}}
            ok, text = c.call("nca_run", args); assert ok, text
            r = json.loads(text); ids.append(r["id"])
            calls.append({"tool": "nca_run", "arguments": args}); results[f"nca_run_{method}"] = r
        for args, key in (({"a": ids[0], "b": ids[1]}, "compare_all"), ({"a": ids[0], "b": ids[1], "parameters": ["auclast"]}, "compare_auclast")):
            ok, text = c.call("analysis_compare", args); assert ok, text
            calls.append({"tool": "analysis_compare", "arguments": args}); results[key + "_result"] = json.loads(text)
        golden = {"case": name, "source": source, "server": c.server_info, "engine_commit": commit, "calls": calls, **results}
    finally: c.close()
    os.makedirs(os.path.join(OUT, "compare"), exist_ok=True)
    with open(os.path.join(OUT, "compare", name + ".json"), "w", encoding="utf-8") as f:
        json.dump(golden, f, ensure_ascii=False, indent=1)
    print("wrote compare/" + name)

def main():
    os.makedirs(OUT, exist_ok=True)
    commit = engine_commit()
    make_compare(commit)
    for name, (source, imp, nca) in CASES.items():
        c = apothicaire.MCPClient([apothicaire.MCP_BIN])
        try:
            ok, text = c.call("data_import", imp); assert ok, text
            ws = json.loads(text); wid = ws["worksheet"]["id"]
            args = {"worksheet": wid, **nca}
            ok2, text2 = c.call("nca_run", args); assert ok2, text2
            golden = {"case": name, "source": source, "server": c.server_info, "engine_commit": commit,
                      "calls": [{"tool": "data_import", "arguments": imp}, {"tool": "nca_run", "arguments": args}],
                      "data_import_result": ws, "nca_run_result": json.loads(text2)}
            if name == "theoph_s1_oral_dose_arg":
                with open(os.path.join(OUT, "tools_list.json"), "w", encoding="utf-8") as f:
                    json.dump({"server": c.server_info, "engine_commit": commit,
                               "tools": c.request("tools/list")["tools"]}, f, ensure_ascii=False, indent=1, sort_keys=True)
        finally: c.close()
        with open(os.path.join(OUT, name + ".json"), "w", encoding="utf-8") as f:
            json.dump(golden, f, ensure_ascii=False, indent=1)
        print("wrote", name)

if __name__ == "__main__":
    main()
