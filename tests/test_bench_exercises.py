"""Tests of the benchmark exercise generator (bench/make_exercises.py). They need the built caladrius-mcp
(skipped without it) but no language model.

Checked: the plan has the requested mix (25 exercises; models, units, BLQ), the generator is deterministic
(two runs into two folders are byte-identical, and the CSV and simulation parameters equal the committed
exercises), and every committed exercise round-trips through data_import + nca_run: the ground truth is
what the engine returns for the written CSV, parameter by parameter, with the arguments stored in meta.json.
"""
import collections, filecmp, json, os, shutil, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
sys.path.insert(0, AGENT)
import apothicaire  # noqa: E402
from bench import make_exercises as mk  # noqa: E402

BUILT = os.path.exists(apothicaire.MCP_BIN)

class TestPlan(unittest.TestCase):
    def test_mix(self):
        self.assertEqual(len(mk.PLAN), 25)
        fam = collections.Counter(r[0] for r in mk.PLAN)
        self.assertEqual(set(fam), {"iv_bolus", "iv_infusion", "oral_1", "oral_1_lag", "oral_0", "pk2_iv_bolus", "pk2_oral_1"})
        self.assertGreaterEqual(min(fam.values()), 3)
        self.assertEqual({r[1] for r in mk.PLAN if r[0].startswith("pk2")}, {"pk2.iv_bolus", "pk2.oral_1"})
        self.assertEqual({r[2] for r in mk.PLAN}, {"mg", "ug"})
        self.assertEqual({r[3] for r in mk.PLAN}, {"mg/L", "ng/mL"})
        self.assertEqual({r[4] for r in mk.PLAN}, {"h", "min"})
        self.assertTrue(1 <= sum(r[5] for r in mk.PLAN) <= 2)                    # one or two BLQ exercises
        self.assertTrue(2 <= sum(r[4] == "min" for r in mk.PLAN) <= 6)           # min for a few
        for r in mk.PLAN: self.assertIn((r[2], r[3]), mk.CONC_FACTOR)

    def test_helpers(self):
        self.assertEqual(mk.sig(0.0123456, 3), 0.0123)
        self.assertEqual(mk.sig(0), 0.0)
        beta, alpha = mk.beta_alpha(2, 10, 4, 8)                                # the engine's public pk2 example
        self.assertAlmostEqual(beta, 0.1); self.assertAlmostEqual(alpha, 1.0)

@unittest.skipUnless(BUILT, "caladrius-mcp is not built")
class TestGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="apo_bench_")
        cls.a, cls.b = os.path.join(cls.tmp, "a"), os.path.join(cls.tmp, "b")
        cls.ids = mk.generate(cls.a)
        mk.generate(cls.b)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_deterministic(self):
        self.assertEqual(len(self.ids), 25)
        self.assertEqual(len(set(self.ids)), 25)
        for i in self.ids:
            for f in ("data.csv", "meta.json"):
                self.assertTrue(filecmp.cmp(os.path.join(self.a, i, f), os.path.join(self.b, i, f), shallow=False), (i, f))

    def test_equals_the_committed_exercises(self):
        self.assertEqual([os.path.basename(d) for d in mk.list_exercises()], self.ids)
        for i in self.ids:
            m0, c0 = mk.load(os.path.join(mk.OUT, i)); m1, c1 = mk.load(os.path.join(self.a, i))
            self.assertEqual(c0, c1, i)
            self.assertEqual(m0["simulation"], m1["simulation"], i)
            self.assertEqual(m0["ground_truth"]["fit_parameters"], m1["ground_truth"]["fit_parameters"], i)

    def test_shape_of_every_exercise(self):
        blq = 0
        for d in mk.list_exercises(self.a):
            m, csv = mk.load(d); lines = csv.strip().split("\n")
            with self.subTest(ex=m["id"]):
                self.assertEqual(lines[0], f"time ({m['units']['time']}),conc ({m['units']['conc']})")
                rows = [[float(x) for x in l.split(",")] for l in lines[1:]]
                self.assertTrue(8 <= len(rows) <= 12); self.assertEqual(len(rows), m["n_points"])
                times = [r[0] for r in rows]
                self.assertEqual(times, sorted(set(times)))
                self.assertTrue(all(r[1] >= 0 for r in rows))
                self.assertTrue(0.05 <= m["noise"]["cv"] <= 0.10)
                self.assertIn(m["dose"]["unit"], ("mg", "ug")); self.assertGreater(m["dose"]["amount"], 0)
                self.assertIn(m["model"], {r[1] for r in mk.PLAN})
                if m["blq"]:
                    blq += 1; self.assertGreaterEqual(sum(1 for r in rows if r[1] == 0), m["blq"]["n_blq"])
                if isinstance(m["route"], dict): self.assertEqual(m["model"], "pk1.iv_infusion")
                if m["model"].startswith("pk2"): self.assertEqual(set(m["simulation"]["parameters"]) & {"cl", "vc", "q", "vp"}, {"cl", "vc", "q", "vp"})
                for method in mk.METHODS:
                    p = m["ground_truth"]["nca"][method]["parameters"]
                    self.assertIn("half.life", p); self.assertIn("auclast", p); self.assertIn("cmax", p)
        self.assertTrue(1 <= blq <= 2)

    def test_round_trip_through_data_import_and_nca_run(self):
        client = apothicaire.MCPClient([apothicaire.MCP_BIN])
        try:
            for d in mk.list_exercises():
                m, csv = mk.load(d)
                imp = {"name": m["id"], "csv": csv, "columns": m["ground_truth"]["data_import_columns"]}
                ok, text = client.call("data_import", imp); self.assertTrue(ok, text)
                ws = json.loads(text)["worksheet"]
                self.assertEqual(ws["rows"], m["n_points"])
                self.assertEqual(ws["derived_units"], m["ground_truth"]["worksheet_derived_units"])
                for method in mk.METHODS:
                    truth = m["ground_truth"]["nca"][method]
                    ok, text = client.call("nca_run", {"worksheet": ws["id"], **truth["nca_run_arguments"]})
                    self.assertTrue(ok, text)
                    got = json.loads(text)["result"]["subjects"][0]["outcome"]["ok"]["parameters"]
                    got = {p["name"]: p["value"]["value"] for p in got if "value" in p["value"]}
                    with self.subTest(ex=m["id"], method=method):
                        self.assertEqual(got, {k: v["value"] for k, v in truth["parameters"].items()})
                        self.assertEqual(truth["nca_run_arguments"]["dose"], m["dose"]["amount"])
                        self.assertEqual(truth["nca_run_arguments"]["route"], m["route"])
        finally:
            client.close()

if __name__ == "__main__":
    unittest.main()
