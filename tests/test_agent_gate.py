"""The gate wired into the agent, with a scripted language model and the REAL caladrius-mcp server
(skipped if the binary is not built). No llama.cpp server is needed: `ag.llm.chat` is replaced.

Checked: one regeneration with the reminder appended at the END of the messages (system prompt and
earlier messages untouched), the better answer kept, the badge on a still-wrong answer, the memory
holding the answer without the badge or the reminder, the counts and findings in the turn's stats.
"""
import json, os, shutil, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import apothicaire, optchat, gate  # noqa: E402
import test_digest as td           # noqa: E402

CASE = td.GOLDENS["theoph_s1_oral_dose_arg"]
IMPORT_ARGS = CASE["calls"][0]["arguments"]
NCA_ARGS = {k: v for k, v in CASE["calls"][1]["arguments"].items() if k != "worksheet"}
USER = "Voici les données de l'exercice (320 mg par voie orale ; temps en h, mg/L) :\n" + IMPORT_ARGS["csv"] + "\nFais l'analyse NCA."

def tool_call(name, args, cid):
    return {"role": "assistant", "content": "", "tool_calls": [
        {"id": cid, "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}]}

def say(text): return {"role": "assistant", "content": text}

class FakeLLM:
    def __init__(self, script):
        self.script, self.calls, self.last, self.total_slots = list(script), [], {}, 2
    def chat(self, messages, slot, tools=None, max_tokens=512, think=False, **kw):
        self.calls.append({"messages": json.loads(json.dumps(messages)), "tools": tools, "slot": slot})
        item = self.script.pop(0)
        if isinstance(item, Exception): raise item
        n = len(self.calls)
        self.last = {"wall_s": 0.1, "prompt_tokens": 1000 * n, "completion_tokens": 10, "prompt_eval_n": 10,
                          "cache_n": 990, "prompt_ms": 1, "predicted_ms": 1, "gen_tps": 20.0, "finish_reason": "stop"}
        return item(messages) if callable(item) else item

def cl_text(ag):
    """'value unit' of cl.obs as shown to the model in the last NCA digest."""
    digest = json.loads(next(c for c in reversed(ag.tool_log) if c["name"] == "nca_run")["shown"])
    return digest["subjects"][0]["parameters"]["cl.obs"]

def fr(s): return s.replace(".", ",")

@unittest.skipUnless(os.path.exists(apothicaire.MCP_BIN), "caladrius-mcp is not built")
class TestAgentGate(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="apo_test_")
        self.ag = None

    def tearDown(self):
        if self.ag:
            self.ag.close()
        shutil.rmtree(self.dir, ignore_errors=True)

    def agent(self):
        """An agent whose model is scripted: two tool rounds (import, NCA); the test appends the answer(s)."""
        cfg = dict(optchat.CFG, data_dir=self.dir)
        ag = apothicaire.Apothicaire(cfg=cfg)
        script = [tool_call("data_import", IMPORT_ARGS, "c1"), tool_call("nca_run", {"worksheet": 1, **NCA_ARGS}, "c2")]
        ag.llm = FakeLLM(script); ag.compactor.llm = ag.llm
        self.ag = ag
        return ag

    def bad_answer(self, ag):
        # the model converts CL/F: value x 1000 in another unit; a correct number comes first
        def f(messages):
            v = cl_text(ag).split()[0]
            return say(f"CL/F = {fr(v)} dose unit/(h·mg/L), soit {fr(str(float(v) * 1000))} L/h.")
        return f

    def good_answer(self, ag):
        def f(messages): return say(f"CL/F = {fr(cl_text(ag))}.")
        return f

    def test_regeneration_fixes_the_answer(self):
        ag = self.agent()
        ag.llm.script += [self.bad_answer(ag), self.good_answer(ag)]
        ans, st = ag.turn(USER, verbose=False)
        calls = ag.llm.calls
        self.assertEqual(len(calls), 4)
        self.assertEqual(ans, f"CL/F = {fr(cl_text(ag))}.")                   # no badge
        # the reminder is appended at the end of the messages of the 4th call; nothing before it changes
        third, fourth = calls[2]["messages"], calls[3]["messages"]
        self.assertEqual(fourth[0], third[0])                                  # the system prompt
        self.assertEqual(fourth[:len(third)], third)                           # the earlier messages
        self.assertEqual([m["role"] for m in fourth[len(third):]], ["assistant", "user"])
        self.assertIn("quote tool values verbatim, never convert", fourth[-1]["content"])
        self.assertIn(fr(str(float(cl_text(ag).split()[0]) * 1000)), fourth[-1]["content"])
        self.assertIsNone(calls[3]["tools"]); self.assertIsNotNone(calls[2]["tools"])
        self.assertEqual(calls[3]["slot"], 0)
        # the memory holds the corrected answer only
        log = ag.store.log
        self.assertEqual(log[-1]["role"], "assistant"); self.assertEqual(log[-1]["content"], ans)
        self.assertFalse(any("system reminder" in m["content"] for m in log))
        g = st["gate"]
        self.assertTrue(g["regenerated"]); self.assertEqual(g["kept"], "regenerated")
        self.assertEqual(g["before"]["numbers_unverified"], 1); self.assertEqual(g["after"]["numbers_unverified"], 0)
        self.assertGreaterEqual(g["before"]["numbers_total"], 2)
        self.assertEqual(g["findings"], []); self.assertEqual(len(g["first_findings"]), 1)
        self.assertIn("hint", g["first_findings"][0]); self.assertIn("first_answer", g)
        self.assertEqual(st["prompt_tokens"], 1000)                            # stats of the turn are those of its own calls: the regeneration is in st["gate"]["regen_stats"]
        self.assertEqual(st["gate"]["regen_stats"]["prompt_tokens"], 4000)
        json.dumps(st)                                                         # the transcript JSON can hold it
        with open(os.path.join(self.dir, "gate.jsonl"), encoding="utf-8") as f:
            self.assertEqual(len(f.readlines()), 1)

    def test_a_clean_answer_costs_no_regeneration(self):
        ag = self.agent(); ag.llm.script += [self.good_answer(ag)]
        ans, st = ag.turn(USER, verbose=False)
        self.assertEqual(len(ag.llm.calls), 3)
        self.assertFalse(st["gate"]["regenerated"]); self.assertEqual(st["gate"]["before"]["numbers_unverified"], 0)
        self.assertNotIn("⚠", ans)

    def test_still_wrong_after_regeneration_gets_a_badge(self):
        ag = self.agent(); ag.llm.script += [self.bad_answer(ag), self.bad_answer(ag)]
        ans, st = ag.turn(USER, verbose=False)
        wrong = fr(str(float(cl_text(ag).split()[0]) * 1000))
        self.assertIn("⚠ 1 number(s) not found in tool results: " + wrong, ans)
        self.assertTrue(ans.index("⚠") > ans.index("L/h."))
        self.assertNotIn("⚠", ag.store.log[-1]["content"])                # the badge is shown, not remembered
        g = st["gate"]
        self.assertEqual((g["before"]["numbers_unverified"], g["after"]["numbers_unverified"]), (1, 1))
        self.assertEqual(g["findings"][0]["number"], wrong)
        self.assertEqual(len(ag.llm.calls), 4)                                 # one regeneration, not more

    def test_a_worse_regeneration_is_not_kept(self):
        ag = self.agent()
        def worse(messages):
            v = cl_text(ag).split()[0]
            return say(f"CL/F {fr(str(float(v) * 1000))} L/h, Vz {fr(str(float(v) * 777))} L, {fr(str(float(v) * 999))} L/h")
        ag.llm.script += [self.bad_answer(ag), worse]
        ans, st = ag.turn(USER, verbose=False)
        self.assertEqual(st["gate"]["kept"], "first"); self.assertTrue(st["gate"]["regenerated"])
        self.assertEqual(st["gate"]["after"]["numbers_unverified"], 1)
        self.assertEqual(st["gate"]["after_regeneration"]["numbers_unverified"], 3)
        self.assertIn("soit", ans)                                              # the first draft

    def test_llm_error_during_regeneration_keeps_the_first_answer(self):
        ag = self.agent(); ag.llm.script += [self.bad_answer(ag), optchat.LLMError("HTTP 500: boom")]
        ans, st = ag.turn(USER, verbose=False)
        self.assertEqual(st["gate"]["kept"], "first"); self.assertIn("error", st["gate"]["regen_stats"])
        self.assertIn("⚠ 1 number(s)", ans)

    def test_a_number_the_user_gave_is_a_source(self):
        ag = self.agent(); ag.llm.script += [say("Dose : 320 mg ; 15 points.")]
        ans, st = ag.turn(USER, verbose=False)
        self.assertEqual(st["gate"]["before"]["numbers_unverified"], 0)


class TestGateContext(unittest.TestCase):
    def test_sources_are_user_messages_and_caladrius_results_only(self):
        log = [{"role": "user", "content": "u1"}, {"role": "tool_call", "content": ""},
               {"role": "tool_result", "name": "nca_run", "content": "R1"},
               {"role": "tool_result", "name": "zoom", "content": "Z (a summary with a wrong number)"},
               {"role": "tool_result", "name": "read_message", "content": "M"},
               {"role": "assistant", "content": "A1 (the model's own words)"},
               {"role": "tool_result", "name": "data_import", "content": "R2"}, {"role": "user", "content": "u2"}]
        tools, users = apothicaire.gate_context(log, {"nca_run": 1, "data_import": 1})
        self.assertEqual(tools, ["R1", "R2"]); self.assertEqual(users, ["u1", "u2"])


class TestStaticPrefixUntouched(unittest.TestCase):
    def test_gate_adds_nothing_to_the_system_prompt_or_the_tool_definitions(self):
        self.assertNotIn("gate", optchat.SYSTEM_PROMPT.lower().replace("investigate", ""))
        self.assertNotIn("system reminder", optchat.SYSTEM_PROMPT)
        self.assertNotIn("system reminder", apothicaire.SYSTEM_ADDITION)


if __name__ == "__main__":
    unittest.main()
