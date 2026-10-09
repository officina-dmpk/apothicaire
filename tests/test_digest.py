"""Golden-file tests of the NCA digest and of the schema flattening.

The golden files (tests/golden/*.json) are frozen answers of the real caladrius-mcp server on PUBLIC
data (caladrius/oracle/data), with the exact tool arguments next to them. The tests need neither the
server nor the language model: they replay the stored answers through the code that builds what the
model is shown. Regenerate the goldens with tests/make_golden.py (by hand, after a deliberate change
of the engine, and review the diff).

What is asserted, for every golden case and subject:
  * every computed parameter appears as "value unit", the value at 6 significant digits (the display
    rounding of the client), the unit taken from the worksheet's units, percentages as "%";
  * no extra parameter: the digest's parameters + not_calculated are exactly the payload's parameters;
  * not-calculated parameters are listed under their reason; flags, options, removed points, the
    selected lambda_z regression, subject, dose, route and errors are reproduced;
  * no number of the digest is absent from the payload (nothing converted, nothing computed).
Run: python -m unittest discover -s tests
"""
import copy, glob, json, os, re, sys, unittest
from decimal import Decimal, ROUND_HALF_EVEN

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
sys.path.insert(0, AGENT)
import apothicaire  # noqa: E402  (imports optchat; no server is contacted at import)

GOLDEN_DIR = os.path.join(HERE, "golden")

def load(name):
    with open(os.path.join(GOLDEN_DIR, name), encoding="utf-8") as f:
        return json.load(f)

def goldens():
    return {os.path.basename(p)[:-5]: load(os.path.basename(p))
            for p in sorted(glob.glob(os.path.join(GOLDEN_DIR, "*.json")))
            if not p.endswith("tools_list.json")}

GOLDENS = goldens()

# ---------------------------------------------------------------- independent expectations
def round6(x):
    """x rounded to 6 significant digits, as an exact Decimal (half-even), independent of the client."""
    d = Decimal(repr(x)) if isinstance(x, float) else Decimal(x)
    if d == 0: return d
    return d.quantize(Decimal(1).scaleb(d.adjusted() - 5), rounding=ROUND_HALF_EVEN)

def sig_digits(token):
    """Significant digits written in a decimal token such as '0.00271828' or '3127.58' or '1e-05'."""
    mant = re.split(r"[eE]", token)[0].replace("-", "").replace("+", "")
    if "." in mant: return len(mant.replace(".", "").lstrip("0"))
    return len(mant.lstrip("0").rstrip("0")) or 1

DIMENSIONLESS = {"r.squared", "adj.r.squared", "span.ratio", "lambda.z.n.points"}
AUC = {"aucall", "auclast", "aucinf.obs", "aucinf.pred", "aucivall", "aucivinf.obs", "aucivinf.pred", "aucivlast"}
AUMC = {"aumcall", "aumclast", "aumcinf.obs", "aumcinf.pred"}
PERCENT = {"aucpext.obs", "aucpext.pred", "aumcpext.obs", "aumcpext.pred", "aucivpbextall", "aucivpbextlast",
           "aucivpbextinf.obs", "aucivpbextinf.pred"}
CONC = {"c0", "cmax", "clast.obs", "clast.pred"}
TIME = {"tfirst", "tlag", "tlast", "tmax", "half.life", "lambda.z.time.first", "lambda.z.time.last",
        "mrt.last", "mrt.obs", "mrt.pred", "mrt.iv.last", "mrt.iv.obs", "mrt.iv.pred"}
CLEARANCE = {"cl.obs", "cl.pred"}
VOLUME = {"vz.obs", "vz.pred", "vss.obs", "vss.pred", "vss.iv.last", "vss.iv.obs", "vss.iv.pred"}

def expected_unit(name, ws):
    """Unit label of a PKNCA parameter from the worksheet answer alone ('' = dimensionless).
    An unknown parameter name fails the test on purpose: extend the table after reading the engine's change."""
    cols = {c["role"]: c.get("unit") for c in ws["columns"]}
    t, c, d = cols["time"], cols["concentration"], cols.get("dose") or "dose unit"
    der = ws["derived_units"]
    if name.endswith(".dn"):
        base = expected_unit(name[:-3], ws)
        return f"{base}/(dose unit)" if base else "per dose unit"
    if name in DIMENSIONLESS: return ""
    if name in PERCENT: return "%"
    if name in AUC: return der["auc"]
    if name in AUMC: return der["aumc"]
    if name in CONC: return c
    if name in TIME: return t
    if name == "lambda.z": return der["lambda_z"]
    if name in CLEARANCE: return der.get("cl") or f"{d}/({t}*{c})"
    if name in VOLUME: return der.get("v") or f"{d}/({c})"
    raise AssertionError(f"parameter {name!r} is not in the test's unit table")

def numbers_of(obj, acc=None):
    """All numbers of a JSON value: numeric leaves and numbers written in string leaves
    (not those glued to a letter, such as the 2 of an identifier)."""
    acc = [] if acc is None else acc
    if isinstance(obj, bool) or obj is None: return acc
    if isinstance(obj, (int, float)): acc.append(Decimal(repr(obj)))
    elif isinstance(obj, str):
        for m in re.finditer(r"(?<![A-Za-z_.\d])\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", obj):
            acc.append(Decimal(m.group(0)))
    elif isinstance(obj, dict):
        for k, v in obj.items(): numbers_of(v, acc)       # keys are names, not numbers
    elif isinstance(obj, list):
        for v in obj: numbers_of(v, acc)
    return acc

def foreign_numbers(digest, payload):
    """Numbers of the digest that are neither a payload number nor a payload number at 6 significant digits."""
    allowed = set()
    for p in numbers_of(payload):
        allowed.add(abs(p)); allowed.add(abs(round6(p)))
    return [n for n in numbers_of(digest) if abs(n) not in allowed]

def split_value(s):
    """'3127.58 h*mg/L' -> (Decimal('3127.58'), 'h*mg/L', '3127.58')."""
    tok, _, unit = s.partition(" ")
    return Decimal(tok), unit, tok

def subject_payloads(g):
    return g["nca_run_result"]["result"]["subjects"]

def digest_of(g):
    ws = g["data_import_result"]["worksheet"]
    cols = {c["role"]: c.get("unit") for c in ws["columns"]}
    units = {"time": cols.get("time"), "conc": cols.get("concentration"), "dose": cols.get("dose"),
             "derived": ws["derived_units"], "warnings": ws.get("unit_warnings", [])}
    return apothicaire.digest_analysis(g["nca_run_result"], units), units

# ---------------------------------------------------------------- tests
class TestGoldenDigest(unittest.TestCase):
    def test_goldens_are_present(self):
        self.assertGreaterEqual(len(GOLDENS), 3)
        for name, g in GOLDENS.items():
            self.assertEqual([c["tool"] for c in g["calls"]], ["data_import", "nca_run"], name)
            self.assertIn("arguments", g["calls"][1], name)

    def test_goldens_cover_the_requested_cases(self):
        names = " ".join(GOLDENS)
        self.assertIn("theoph", names); self.assertIn("indometh", names); self.assertIn("edge_blq", names)
        theoph = GOLDENS["theoph_s1_oral_dose_arg"]
        self.assertIn("dose", theoph["calls"][1]["arguments"])                  # a dose argument
        cols = theoph["calls"][0]["arguments"]["columns"]
        self.assertTrue(all(c.get("unit") for c in cols))                       # explicit units
        self.assertNotIn("dose", theoph["calls"][0]["arguments"]["csv"].splitlines()[0])

    def test_parameters_value_and_unit(self):
        for name, g in GOLDENS.items():
            d, _ = digest_of(g); ws = g["data_import_result"]["worksheet"]
            for sp, sd in zip(subject_payloads(g), d["subjects"]):
                ok = sp["outcome"].get("ok")
                if ok is None: continue
                computed = {p["name"]: p["value"]["value"] for p in ok["parameters"] if "value" in p["value"]}
                with self.subTest(case=name, subject=sp["subject"]):
                    self.assertEqual(set(sd["parameters"]), set(computed))
                    for pname, v in computed.items():
                        shown = sd["parameters"][pname]
                        unit = expected_unit(pname, ws)
                        if unit == "":
                            self.assertIsInstance(shown, float, pname)         # dimensionless: a bare number
                            val, tok = Decimal(repr(shown)), repr(shown)
                        else:
                            self.assertIsInstance(shown, str, pname)
                            val, u, tok = split_value(shown)
                            self.assertEqual(u, unit, f"{pname}: unit")
                        self.assertEqual(val, round6(v), f"{pname}: value {shown!r} vs payload {v!r}")
                        self.assertLessEqual(sig_digits(tok), 6, f"{pname}: more than 6 significant digits")

    def test_percentages(self):
        n = 0
        for name, g in GOLDENS.items():
            d, _ = digest_of(g)
            for sd in d["subjects"]:
                for pname, shown in sd.get("parameters", {}).items():
                    if "pext" in pname or "pbext" in pname:
                        n += 1; self.assertTrue(shown.endswith(" %"), f"{name} {pname}: {shown!r}")
        self.assertGreater(n, 0)

    def test_not_calculated_listed_with_reason(self):
        seen_reasons = set()
        for name, g in GOLDENS.items():
            d, _ = digest_of(g)
            for sp, sd in zip(subject_payloads(g), d["subjects"]):
                ok = sp["outcome"].get("ok")
                if ok is None: continue
                want = {}
                for p in ok["parameters"]:
                    if "value" not in p["value"]: want.setdefault(p["value"]["not_calculated"], []).append(p["name"])
                with self.subTest(case=name, subject=sp["subject"]):
                    self.assertEqual(sd["not_calculated"], want)
                    self.assertFalse(set(sd["parameters"]) & {n for ns in want.values() for n in ns})
                    self.assertEqual(len(sd["parameters"]) + sum(len(v) for v in want.values()), len(ok["parameters"]))
                seen_reasons |= set(want)
        self.assertIn("not_applicable_to_route", seen_reasons)
        self.assertIn("no_rise", seen_reasons)                  # a reason other than the route is covered

    def test_lambda_z_regression(self):
        n = 0
        for name, g in GOLDENS.items():
            d, _ = digest_of(g)
            for sp, sd in zip(subject_payloads(g), d["subjects"]):
                ok = sp["outcome"].get("ok")
                if ok is None: continue
                sel = [c for c in ok["lambda_z_candidates"] if c.get("selected")]
                with self.subTest(case=name, subject=sp["subject"]):
                    if not sel:
                        self.assertNotIn("lambda_z_regression", sd); continue
                    n += 1; self.assertEqual(len(sel), 1)
                    want = {k: v for k, v in sel[0].items() if k not in ("selected", "valid")}
                    got = sd["lambda_z_regression"]
                    self.assertEqual(set(got), set(want))
                    for k, v in want.items():
                        self.assertEqual(Decimal(repr(got[k])), round6(v), k)
        self.assertGreater(n, 0)

    def test_options_flags_removed_points_and_identity(self):
        for name, g in GOLDENS.items():
            d, units = digest_of(g); spec = g["nca_run_result"]["spec"]
            with self.subTest(case=name):
                self.assertEqual(d["analysis"], g["nca_run_result"]["id"])
                self.assertEqual(d["label"], g["nca_run_result"]["label"])
                self.assertEqual(d["status"], g["nca_run_result"]["status"]["state"])
                self.assertEqual(d["options_used"], {"auc_method": spec["options"]["auc_method"],
                                                     "lambda_z": spec["options"]["lambda_z"],
                                                     "quality_thresholds": spec["options"]["quality"],
                                                     "blq": spec["options"]["blq"],
                                                     "missing": spec["options"]["missing"],
                                                     "negative": spec["options"]["negative"],
                                                     "start": spec["options"]["start"]})
                self.assertEqual(d["unit_warnings"], g["data_import_result"]["worksheet"].get("unit_warnings", []))
                self.assertEqual(d["options_used"]["auc_method"], g["calls"][1]["arguments"]["options"]["auc_method"])
                if units["dose"]: self.assertEqual(d["dose_unit"], units["dose"])
                else: self.assertTrue(d["dose_unit"].startswith("unknown to Caladrius"))
            for sp, sd in zip(subject_payloads(g), d["subjects"]):
                with self.subTest(case=name, subject=sp["subject"]):
                    self.assertEqual((sd["subject"], sd["dose"], sd["route"]), (sp["subject"], sp["dose"], sp["route"]))
                    ok = sp["outcome"].get("ok")
                    if ok is None:
                        self.assertEqual(sd["outcome"], sp["outcome"]); continue
                    self.assertEqual(sd["flags"], ok["flags"])
                    self.assertEqual(sd["flag_messages"], sp["flag_messages"])
                    grouped = {}
                    for pname, msg in sp["not_calculated_messages"].items(): grouped.setdefault(msg, []).append(pname)
                    self.assertEqual(sd["not_calculated_messages"], grouped)
                    self.assertEqual({n for ns in sd["not_calculated_messages"].values() for n in ns},
                                     {n for ns in sd["not_calculated"].values() for n in ns})
                    if ok["removed"]: self.assertEqual(sd["removed_points"], ok["removed"])
                    else: self.assertNotIn("removed_points", sd)

    def test_flags_and_removed_points_present_in_the_edge_case(self):
        d, _ = digest_of(GOLDENS["edge_blq_6_subjects"])
        codes = {f["code"] for sd in d["subjects"] for f in sd["flags"]}
        self.assertEqual(codes, {"short_span", "high_extrapolation"})
        self.assertIn("blq", {r["reason"] for sd in d["subjects"] for r in sd.get("removed_points", [])})

    def test_messages_and_unit_warnings_are_carried(self):
        """flag_messages (with their numbers), not_calculated_messages and the worksheet's unit_warnings
        reach the model; a dose with no unit gives a missing_unit warning, a clean worksheet none."""
        d, _ = digest_of(GOLDENS["theoph_s1_oral_dose_arg"])
        self.assertEqual([w["code"] for w in d["unit_warnings"]], ["missing_unit"])
        sd = d["subjects"][0]
        self.assertTrue(any("31.2 %" in m for m in sd["flag_messages"]), sd["flag_messages"])
        self.assertIn("not defined for this route of administration", sd["not_calculated_messages"])
        self.assertIn("c0", sd["not_calculated_messages"]["not defined for this route of administration"])
        d, _ = digest_of(GOLDENS["edge_blq_6_subjects"])
        self.assertEqual(d["unit_warnings"], [])
        self.assertEqual(d["options_used"]["blq"], {"position": {"first": "keep", "last": "keep", "middle": "drop"}})
        self.assertEqual((d["options_used"]["missing"], d["options_used"]["negative"], d["options_used"]["start"]),
                         ("drop", "error", "c0"))

    def test_mass_mismatch_warning_reaches_the_digest(self):
        """A synthetic worksheet answer carrying a mass_mismatch (dose in mg, concentration per ng) is
        remembered by render_tool_result and printed in the next digest."""
        g = GOLDENS["theoph_s1_oral_dose_arg"]
        ws = copy.deepcopy(g["data_import_result"])
        warn = {"code": "mass_mismatch", "message": "dose in mg but concentration per ng"}
        ws["worksheet"]["unit_warnings"] = [warn]
        units = {}
        apothicaire.render_tool_result("data_import", True, json.dumps(ws), units)
        shown = json.loads(apothicaire.render_tool_result("nca_run", True, json.dumps(g["nca_run_result"]), units))
        self.assertEqual(shown["unit_warnings"], [warn])

    def test_subject_errors_are_reproduced(self):
        g = GOLDENS["edge_negative_subject_errors"]
        d, _ = digest_of(g)
        self.assertTrue(all("error" in sd["outcome"] and "parameters" not in sd for sd in d["subjects"]))
        self.assertIn("negative", d["subjects"][0]["outcome"]["error"])

    def test_units_are_labels_never_conversions(self):
        """The same engine number keeps its unit: the dose given as an argument leaves CL and V in
        'dose unit/...', a dose column in mg makes them L/h and L. Nothing is ever multiplied."""
        d, _ = digest_of(GOLDENS["theoph_s1_oral_dose_arg"])
        p = d["subjects"][0]["parameters"]
        self.assertTrue(p["cl.obs"].endswith(" dose unit/(h*mg/L)"), p["cl.obs"])
        self.assertTrue(p["vz.obs"].endswith(" dose unit/(mg/L)"), p["vz.obs"])
        self.assertTrue(p["auclast"].endswith(" h*mg/L"))
        d, _ = digest_of(GOLDENS["edge_blq_6_subjects"])
        p = d["subjects"][0]["parameters"]
        self.assertTrue(p["cl.obs"].endswith(" L/h"), p["cl.obs"]); self.assertTrue(p["vz.obs"].endswith(" L"))
        d, _ = digest_of(GOLDENS["indometh_s1_iv_bolus"])
        p = d["subjects"][0]["parameters"]
        self.assertIn("c0", p); self.assertTrue(p["c0"].endswith(" mg/L"))
        self.assertTrue(p["vss.iv.obs"].endswith(" L"))

    def test_no_number_in_the_digest_is_absent_from_the_payload(self):
        for name, g in GOLDENS.items():
            d, _ = digest_of(g)
            payload = {"nca": g["nca_run_result"], "worksheet": g["data_import_result"]}
            with self.subTest(case=name):
                self.assertEqual(foreign_numbers(d, payload), [])

    def test_foreign_number_detector_works(self):
        """The check above would be vacuous if it could not fail: tamper with a value, a unit factor and a regression."""
        g = GOLDENS["theoph_s1_oral_dose_arg"]
        d, _ = digest_of(g); payload = {"nca": g["nca_run_result"], "worksheet": g["data_import_result"]}
        bad = copy.deepcopy(d); p = bad["subjects"][0]["parameters"]
        val, unit, _ = split_value(p["cl.obs"])
        p["cl.obs"] = f"{val * 1000} mg/(h*ng/mL)"                                   # a unit conversion
        p["cmax"] = "99.9 mg/L"                                                      # an invented value
        bad["subjects"][0]["lambda_z_regression"]["n_points"] = 99
        found = {str(x) for x in foreign_numbers(bad, payload)}
        self.assertEqual(len(found), 3, found)

    def test_replay_through_render_tool_result(self):
        """The model is shown the digest only after the units of the worksheet answer were remembered."""
        for name, g in GOLDENS.items():
            units = {}
            shown_ws = apothicaire.render_tool_result("data_import", True, json.dumps(g["data_import_result"], indent=2), units)
            self.assertEqual(json.loads(shown_ws), g["data_import_result"])         # worksheet answers pass through
            self.assertEqual(list(units), [g["data_import_result"]["worksheet"]["id"]])
            shown = apothicaire.render_tool_result("nca_run", True, json.dumps(g["nca_run_result"], indent=2), units)
            expected, _ = digest_of(g)
            with self.subTest(case=name):
                self.assertEqual(json.loads(shown), json.loads(json.dumps(expected)))
                if any("ok" in sp["outcome"] for sp in subject_payloads(g)):             # (an all-error answer is already small)
                    self.assertLess(len(shown), len(json.dumps(g["nca_run_result"])) / 2)   # a digest, not a copy
                self.assertNotIn("\n", shown)                                            # compact JSON

    def test_errors_and_unparsable_answers_pass_through(self):
        self.assertEqual(apothicaire.render_tool_result("nca_run", False, "boom", {}), "boom")
        self.assertEqual(apothicaire.render_tool_result("nca_run", True, "not json", {}), "not json")


def load_compare():
    with open(os.path.join(GOLDEN_DIR, "compare", "theoph_s1_compare_linear_vs_lin_up_log_down.json"), encoding="utf-8") as f:
        return json.load(f)

COMPARE = load_compare()

def compare_units():
    """The units the client remembers after the three calls that precede analysis_compare (as the agent does)."""
    units = {}
    apothicaire.render_tool_result("data_import", True, json.dumps(COMPARE["data_import_result"]), units)
    for k in ("nca_run_linear", "nca_run_lin_up_log_down"):
        apothicaire.render_tool_result("nca_run", True, json.dumps(COMPARE[k]), units)
    return units

def fmt6(x):
    """A float at 6 significant digits the way the digest writes it (independent: Decimal, then Python's repr of the float)."""
    return repr(float(round6(x)))

class TestCompareDigest(unittest.TestCase):
    """Golden test of the digest of analysis_compare on PUBLIC data: Theoph subject 1 (dose as an argument), the
    same worksheet analysed with the linear and the lin-up/log-down AUC, then the compare tool through the MCP client."""
    def test_golden_shape(self):
        self.assertEqual([c["tool"] for c in COMPARE["calls"]], ["data_import", "nca_run", "nca_run", "analysis_compare", "analysis_compare"])
        self.assertEqual([c["arguments"]["options"]["auc_method"] for c in COMPARE["calls"][1:3]], ["linear", "lin_up_log_down"])
        self.assertEqual(COMPARE["calls"][3]["arguments"], {"a": COMPARE["nca_run_linear"]["id"], "b": COMPARE["nca_run_lin_up_log_down"]["id"]})
        self.assertEqual(COMPARE["calls"][4]["arguments"]["parameters"], ["auclast"])

    def test_one_parameter_line_per_value_unit_difference_percent_ratio(self):
        row = COMPARE["compare_auclast_result"]["rows"][0]
        shown = json.loads(apothicaire.render_tool_result("analysis_compare", True, json.dumps(COMPARE["compare_auclast_result"]), compare_units()))
        unit = COMPARE["data_import_result"]["worksheet"]["derived_units"]["auc"]
        want = (f"a {fmt6(row['a'])} {unit} | b {fmt6(row['b'])} {unit} | difference {fmt6(row['difference'])} {unit} | "
                f"percent {fmt6(row['relative_percent'])} % | ratio {fmt6(row['ratio'])}")
        self.assertEqual(shown["parameters"], {"auclast": want})
        self.assertEqual(shown["not_comparable"], {})
        self.assertEqual((shown["a"]["analysis"], shown["b"]["analysis"]), (COMPARE["nca_run_linear"]["id"], COMPARE["nca_run_lin_up_log_down"]["id"]))
        self.assertEqual(shown["subject"], "1")
        # the engine's own arithmetic, not the digest's: b - a, (b - a) / a * 100, b / a
        self.assertAlmostEqual(row["difference"], row["b"] - row["a"], places=9)
        self.assertAlmostEqual(row["relative_percent"], (row["b"] - row["a"]) / row["a"] * 100, places=9)
        self.assertAlmostEqual(row["ratio"], row["b"] / row["a"], places=12)

    def test_all_rows(self):
        payload = COMPARE["compare_all_result"]; ws = COMPARE["data_import_result"]["worksheet"]
        shown = json.loads(apothicaire.render_tool_result("analysis_compare", True, json.dumps(payload), compare_units()))
        lines, grouped = {}, {}
        for r in payload["rows"]:
            if r["a"] is None and r["b"] is None: grouped.setdefault(r["not_comparable"], []).append(r["parameter"]); continue
            u = expected_unit(r["parameter"], ws)
            parts = [f"a {fmt6(r['a'])}" + (f" {u}" if u else ""), f"b {fmt6(r['b'])}" + (f" {u}" if u else "")]
            if r["difference"] is not None: parts.append(f"difference {fmt6(r['difference'])}" + (f" {u}" if u else ""))
            if r["relative_percent"] is not None: parts.append(f"percent {fmt6(r['relative_percent'])} %")
            if r["ratio"] is not None: parts.append(f"ratio {fmt6(r['ratio'])}")
            if r["not_comparable"]: parts.append(f"not comparable: {r['not_comparable']}")
            lines[r["parameter"]] = " | ".join(parts)
        self.assertEqual(shown["parameters"], lines)
        self.assertEqual(shown["not_comparable"], grouped)
        self.assertTrue(any("a is zero" in l for l in lines.values()))          # a row with a difference but no percentage
        self.assertEqual(len(grouped), 1)                                       # the route-dependent parameters share one reason
        self.assertEqual(len(shown["parameters"]) + sum(len(v) for v in grouped.values()), len(payload["rows"]))
        self.assertLess(len(json.dumps(shown)), len(json.dumps(payload)) / 2)   # a digest, not a copy

    def test_no_number_of_the_digest_is_absent_from_the_payload(self):
        for key in ("compare_auclast_result", "compare_all_result"):
            shown = json.loads(apothicaire.render_tool_result("analysis_compare", True, json.dumps(COMPARE[key]), compare_units()))
            with self.subTest(case=key):
                self.assertEqual(foreign_numbers(shown, COMPARE[key]), [])
        # the detector can fail: a recomputed difference and a converted ratio are foreign
        shown = json.loads(apothicaire.render_tool_result("analysis_compare", True, json.dumps(COMPARE["compare_auclast_result"]), compare_units()))
        shown["parameters"]["auclast"] = shown["parameters"]["auclast"].replace("difference -1.6883", "difference -1.69").replace("ratio 0.988663", "ratio 98.8663")
        self.assertEqual(len(foreign_numbers(shown, COMPARE["compare_auclast_result"])), 2)

    def test_units_come_from_the_engine_when_it_has_them_and_never_from_two_worksheets(self):
        payload = copy.deepcopy(COMPARE["compare_auclast_result"]); row = payload["rows"][0]
        row.update(unit_a="ng*h/mL", unit_b="ng*h/mL", difference_unit="ng*h/mL")
        shown = json.loads(apothicaire.render_tool_result("analysis_compare", True, json.dumps(payload), compare_units()))
        self.assertIn("a 148.923 ng*h/mL | b 147.235 ng*h/mL | difference -1.6883 ng*h/mL", shown["parameters"]["auclast"])
        units = compare_units(); units[("analysis", COMPARE["nca_run_lin_up_log_down"]["id"])] = 99     # another worksheet: no label
        shown = json.loads(apothicaire.render_tool_result("analysis_compare", True, json.dumps(COMPARE["compare_auclast_result"]), units))
        self.assertEqual(shown["parameters"]["auclast"].count("h*mg/L"), 0)
        self.assertTrue(shown["parameters"]["auclast"].startswith("a 148.923 | b 147.235 | difference -1.6883 | percent"))

    def test_unit_mismatch_and_missing_values_are_reported_as_the_engine_says(self):
        rows = [{"parameter": "auclast", "a": 10.0, "b": 12.0, "unit_a": "h*mg/L", "unit_b": "h*ng/mL", "difference": None,
                 "difference_unit": None, "relative_percent": None, "ratio": None,
                 "not_comparable": "unit mismatch: a is in `h*mg/L`, b is in `h*ng/mL`; no unit is converted"},
                {"parameter": "tlag", "a": None, "b": 1.0, "unit_a": "h", "unit_b": "h", "difference": None, "difference_unit": None,
                 "relative_percent": None, "ratio": None, "not_comparable": "analysis a: not calculated"}]
        payload = {"a": {"analysis": 2, "label": "x", "status": "fresh", "subject": "1"}, "b": {"analysis": 3, "label": "y", "status": "fresh", "subject": "1"}, "rows": rows}
        shown = json.loads(apothicaire.render_tool_result("analysis_compare", True, json.dumps(payload), {}))
        self.assertEqual(shown["parameters"]["auclast"], "a 10.0 h*mg/L | b 12.0 h*ng/mL | not comparable: unit mismatch: a is in `h*mg/L`, b is in `h*ng/mL`; no unit is converted")
        self.assertEqual(shown["parameters"]["tlag"], "a none | b 1.0 h | not comparable: analysis a: not calculated")
        self.assertNotIn("difference", shown["parameters"]["auclast"])

    def test_errors_pass_through(self):
        self.assertEqual(apothicaire.render_tool_result("analysis_compare", False, "ambiguous_subject: 6 subjects", {}), "ambiguous_subject: 6 subjects")

    def test_tool_and_prompt(self):
        tools = {t["name"]: t for t in load("tools_list.json")["tools"]}
        f = apothicaire.to_openai(tools["analysis_compare"])["function"]
        self.assertEqual(f["parameters"]["required"], ["a", "b"])
        self.assertEqual({k: v["type"] for k, v in f["parameters"]["properties"].items()}, {"a": "integer", "b": "integer", "parameters": "array"})
        self.assertEqual(f["parameters"]["properties"]["parameters"]["items"], {"type": "string"})
        self.assertIn("analysis_compare", apothicaire.EXPOSED)
        self.assertIn("Differences, percentages and ratios between two results come from analysis_compare", apothicaire.SYSTEM_ADDITION)
        self.assertLess(len(json.dumps(f)), 1200)


class TestSchemaFlattening(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.listing = load("tools_list.json")
        cls.tools = {t["name"]: t for t in cls.listing["tools"]}

    @staticmethod
    def keys_anywhere(obj, found=None):
        found = set() if found is None else found
        if isinstance(obj, dict):
            for k, v in obj.items(): found.add(k); TestSchemaFlattening.keys_anywhere(v, found)
        elif isinstance(obj, list):
            for v in obj: TestSchemaFlattening.keys_anywhere(v, found)
        return found

    def test_inline_resolves_refs_and_drops_metadata(self):
        defs = {"Id": {"type": "integer", "minimum": 1, "description": "an id"},
                "Mode": {"enum": ["a", "b"], "type": "string"}}
        schema = {"$schema": "x", "title": "t", "$defs": defs, "type": "object", "properties": {
            "w": {"$ref": "#/$defs/Id"}, "o": {"$ref": "#/$defs/Id", "description": "mine"},
            "l": {"type": "array", "items": {"$ref": "#/$defs/Mode"}},
            "u": {"anyOf": [{"$ref": "#/$defs/Mode"}, {"type": "null"}]}}}
        out = apothicaire._inline(schema, schema["$defs"])
        self.assertEqual(out["properties"]["w"], {"type": "integer", "minimum": 1, "description": "an id"})
        self.assertEqual(out["properties"]["o"]["description"], "mine")             # a sibling overrides the target
        self.assertEqual(out["properties"]["o"]["minimum"], 1)
        self.assertEqual(out["properties"]["l"]["items"], {"enum": ["a", "b"], "type": "string"})
        self.assertEqual(out["properties"]["u"]["anyOf"][0], {"enum": ["a", "b"], "type": "string"})
        self.assertFalse({"$ref", "$defs", "$schema", "title"} & self.keys_anywhere(out))

    def test_inline_resolves_nested_refs(self):
        defs = {"A": {"type": "object", "properties": {"b": {"$ref": "#/$defs/B"}}}, "B": {"type": "number"}}
        out = apothicaire._inline({"$ref": "#/$defs/A"}, defs)
        self.assertEqual(out, {"type": "object", "properties": {"b": {"type": "number"}}})

    def test_stored_listing_is_the_full_server_surface(self):
        self.assertEqual(self.listing["server"]["name"], "caladrius-mcp")
        for n in apothicaire.EXPOSED: self.assertIn(n, self.tools)
        self.assertTrue(any("$ref" in json.dumps(t["inputSchema"]) for t in self.tools.values()))   # the input does need flattening

    def test_to_openai_on_every_exposed_tool(self):
        for n in apothicaire.EXPOSED:
            tool = self.tools[n]; before = copy.deepcopy(tool)
            f = apothicaire.to_openai(tool)
            with self.subTest(tool=n):
                self.assertEqual(tool, before)                                       # the stored schema is not mutated
                self.assertEqual(f["type"], "function"); self.assertEqual(f["function"]["name"], n)
                params = f["function"]["parameters"]
                self.assertFalse({"$ref", "$defs", "$schema", "title"} & self.keys_anywhere(params))
                self.assertEqual(params["type"], "object")
                self.assertEqual(params["required"], tool["inputSchema"]["required"])
                self.assertNotIn("Command `", f["function"]["description"])
                self.assertTrue(f["function"]["description"])
                json.dumps(f)                                                         # serialisable as is

    def test_nca_run_function(self):
        f = apothicaire.to_openai(self.tools["nca_run"])["function"]["parameters"]["properties"]
        self.assertEqual(set(f["options"]["properties"]), set(apothicaire.NCA_OPTIONS_KEPT))
        self.assertEqual(f["options"]["properties"]["auc_method"]["enum"], ["linear", "lin_up_log_down", "lin_log"])
        self.assertEqual(f["options"]["properties"]["lambda_z"]["properties"]["min_points"],
                         {"minimum": 3, "type": "integer"})
        q = f["options"]["properties"]["quality"]["properties"]
        self.assertEqual(set(q), {"max_extrapolated_percent", "min_adj_r_squared", "min_points", "min_span_ratio"})
        self.assertEqual(f["route"]["enum"], ["extravascular", "iv_bolus", "iv_infusion"])
        self.assertEqual(f["infusion_duration"]["type"], "number")                       # the model never writes the route object
        self.assertNotIn("anyOf", f["route"])
        self.assertEqual(f["dose"]["type"], "number")
        self.assertEqual(f["worksheet"]["minimum"], 1); self.assertEqual(f["worksheet"]["type"], "integer")
        self.assertEqual(f["analysis"]["type"], "integer")
        self.assertIn("subject", f)

    def test_data_import_function(self):
        f = apothicaire.to_openai(self.tools["data_import"])["function"]["parameters"]
        self.assertEqual(set(f["properties"]), {"name", "csv", "columns"})          # decimal_comma, delimiter hidden
        role = f["properties"]["columns"]["items"]["properties"]["role"]
        self.assertEqual(role["enum"], ["time", "concentration", "subject", "dose", "route", "other"])

    def test_export_and_analysis_get(self):
        f = apothicaire.to_openai(self.tools["export_table"])["function"]["parameters"]["properties"]
        self.assertIn("nca.parameters", f["table"]["enum"])
        self.assertEqual(f["analysis"]["minimum"], 1)
        g = apothicaire.to_openai(self.tools["analysis_get"])["function"]["parameters"]["properties"]
        self.assertEqual(g["analysis"]["type"], "integer")


if __name__ == "__main__":
    unittest.main()
