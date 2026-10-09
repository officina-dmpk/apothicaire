"""The infusion route: the model writes route = "iv_infusion" and infusion_duration (a string enum and a number);
the client builds the server's {"iv_infusion": {"duration": d}}. Needs the built caladrius-mcp (real server, no model)."""
import json, os, shutil, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import apothicaire, optchat  # noqa: E402
import test_digest as td  # noqa: E402

IMPORT = td.GOLDENS["theoph_s1_oral_dose_arg"]["calls"][0]["arguments"]

class TestRouteArguments(unittest.TestCase):
    def test_translation_without_a_server(self):
        f = apothicaire.Apothicaire._nca_route
        a = {"worksheet": 1, "route": "iv_infusion", "infusion_duration": 2}
        self.assertIsNone(f(a)); self.assertEqual(a["route"], {"iv_infusion": {"duration": 2}}); self.assertNotIn("infusion_duration", a)
        a = {"route": "extravascular", "infusion_duration": 2}
        self.assertIsNone(f(a)); self.assertEqual(a, {"route": "extravascular"})              # ignored with another route
        a = {"route": '{"iv_infusion": {"duration": 1.5}}'}
        self.assertIsNone(f(a)); self.assertEqual(a["route"], {"iv_infusion": {"duration": 1.5}})   # a stringified object is parsed
        for bad in ({"route": "iv_infusion"}, {"route": "iv_infusion", "infusion_duration": 0}, {"route": "iv_infusion", "infusion_duration": "2"},
                    {"route": "iv_infusion", "infusion_duration": True}):
            self.assertTrue(f(dict(bad)).startswith("TOOL ERROR"), bad)
        self.assertTrue(f({"route": "{not json"}).startswith("TOOL ERROR"))
        a = {"route": "iv_bolus"}; self.assertIsNone(f(a)); self.assertEqual(a, {"route": "iv_bolus"})

@unittest.skipUnless(os.path.exists(apothicaire.MCP_BIN), "caladrius-mcp is not built")
class TestRouteWithTheServer(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="apo_route_")
        self.ag = apothicaire.Apothicaire(cfg=dict(optchat.CFG, data_dir=self.dir))
        self.ag._tool("data_import", IMPORT)

    def tearDown(self):
        self.ag.close(); shutil.rmtree(self.dir, ignore_errors=True)

    def test_infusion_reaches_the_engine(self):
        out = self.ag._tool("nca_run", {"worksheet": 1, "dose": 320, "route": "iv_infusion", "infusion_duration": 1.5,
                                        "options": {"auc_method": "linear"}})
        d = json.loads(out)
        self.assertEqual(d["subjects"][0]["route"], {"iv_infusion": {"duration": 1.5}})
        call = self.ag.tool_log[-1]
        self.assertTrue(call["ok"]); self.assertEqual(call["args"]["route"], {"iv_infusion": {"duration": 1.5}})
        self.assertNotIn("infusion_duration", call["args"])

    def test_missing_duration_is_an_error_the_model_can_read(self):
        n = len(self.ag.tool_log)
        out = self.ag._tool("nca_run", {"worksheet": 1, "dose": 320, "route": "iv_infusion"})
        self.assertIn("infusion_duration", out); self.assertEqual(len(self.ag.tool_log), n)        # no call reached the server

if __name__ == "__main__":
    unittest.main()
