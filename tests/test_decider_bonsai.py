"""Tests of the 27B control decider (decision/decider_bonsai.py) against a fake llama.cpp server. No model, no GPU, synthetic state only.

* the prompt builder: the state comes first, every question with its options and their descriptions after it, the schema constrains each key;
* the parser: valid answers, a boolean for a noul question, a value outside the options, a missing key, unparsable text, a fenced object;
* the decider against a fake OpenAI-style server: one call per row, one call per question, invalid answers recorded and counted, raw outputs logged.
"""
import http.server, json, os, sys, tempfile, threading, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
sys.path.insert(0, AGENT); sys.path.insert(0, os.path.join(AGENT, "decision"))
import decider_bonsai as B  # noqa: E402

STATE = {"analyses": [{"auc_method": "linear", "id": 2, "kind": "nca"}],
         "data": {"first_rows": ["0,0", "1,5.2"], "header": "time (h),conc (ng/mL)", "n_rows": 12, "n_subjects": 1},
         "notes": [], "request": "et la t1/2 ?", "user_dose_sentence": "400 mg par voie orale"}
QS = {"route": {"type": "choice", "instructions": "Which route?",
                "criteria": {"oral": "Oral administration.", "iv_bolus": "Intravenous bolus.", "unknown": "Not stated."}},
      "asked_cmax": {"type": "noul", "instructions": "The request asks for Cmax.", "criteria": {"false": "No.", "true": "Yes."}}}


class FakeServer:
    """Answers every chat completion with `replies` in turn (a callable of the request body, or a string); records the bodies."""
    def __init__(self, reply):
        self.bodies, outer = [], self
        class H(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                outer.bodies.append(body)
                text = reply(body) if callable(reply) else reply
                out = json.dumps({"choices": [{"message": {"content": text}, "finish_reason": "stop"}],
                                  "usage": {"prompt_tokens": 100, "completion_tokens": 10}}).encode()
                self.send_response(200); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(out)))
                self.end_headers(); self.wfile.write(out)
            def log_message(self, *a): pass
        self.httpd = http.server.HTTPServer(("127.0.0.1", 0), H)
        self.url = "http://127.0.0.1:%d" % self.httpd.server_port
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
    def close(self): self.httpd.shutdown(); self.httpd.server_close()


def echo_first_option(body):
    """A well-behaved server: for each key of the schema, the first option of its enum."""
    props = body["response_format"]["json_schema"]["schema"]["properties"]
    return json.dumps({k: v["enum"][0] for k, v in props.items()})


class PromptTest(unittest.TestCase):
    def test_messages(self):
        m = B.build_messages(STATE, QS)
        self.assertEqual([x["role"] for x in m], ["system", "user"])
        u = m[1]["content"]
        self.assertTrue(u.startswith("State:\n"))
        self.assertIn("et la t1/2 ?", u)
        self.assertLess(u.index("et la t1/2 ?"), u.index('Question "route"'))                     # state first, questions last
        self.assertIn("  - iv_bolus: Intravenous bolus.", u)                                      # option with its description
        self.assertIn("  - true: Yes.", u)
        self.assertIn('"route", "asked_cmax"', u)
        self.assertNotIn("think", u.lower().replace("thinking", ""))                              # no chain-of-thought request
        self.assertIn("no reasoning", m[0]["content"])

    def test_single_question_message(self):
        u = B.build_messages(STATE, {"route": QS["route"]})[1]["content"]
        self.assertIn('with the key "route"', u)
        self.assertNotIn("asked_cmax", u)

    def test_state_prefix_is_shared_between_questions(self):
        a = B.build_messages(STATE, {"route": QS["route"]})[1]["content"]
        b = B.build_messages(STATE, {"asked_cmax": QS["asked_cmax"]})[1]["content"]
        self.assertEqual(a[:a.index("Answer the question")], b[:b.index("Answer the question")])

    def test_schema(self):
        s = B.schema_of(QS)
        self.assertEqual(s["required"], ["route", "asked_cmax"])
        self.assertFalse(s["additionalProperties"])
        self.assertEqual(s["properties"]["route"]["enum"], ["oral", "iv_bolus", "unknown"])
        self.assertEqual(s["properties"]["asked_cmax"]["enum"], ["false", "true"])


class ParserTest(unittest.TestCase):
    def test_valid(self):
        a, bad = B.parse('{"route": "oral", "asked_cmax": "true"}', QS)
        self.assertEqual(a, {"route": "oral", "asked_cmax": "true"}); self.assertEqual(bad, [])

    def test_fenced_and_embedded_object(self):
        self.assertEqual(B.parse('```json\n{"route": "oral", "asked_cmax": "false"}\n```', QS)[1], [])
        self.assertEqual(B.parse('Sure! {"route": "oral", "asked_cmax": "false"} done', QS)[1], [])

    def test_boolean_for_noul_is_the_same_answer(self):
        a, bad = B.parse('{"route": "oral", "asked_cmax": true}', QS)
        self.assertEqual(a["asked_cmax"], "true"); self.assertEqual(bad, [])

    def test_outside_options_is_invalid_not_repaired(self):
        a, bad = B.parse('{"route": "per os", "asked_cmax": "true"}', QS)
        self.assertNotIn("route", a)
        self.assertEqual(bad, [{"question": "route", "value": "per os", "reason": "outside options"}])
        a, bad = B.parse('{"route": "Oral", "asked_cmax": "true"}', QS)                        # no case folding either
        self.assertEqual([b["question"] for b in bad], ["route"])

    def test_missing_key(self):
        a, bad = B.parse('{"route": "oral"}', QS)
        self.assertEqual(bad, [{"question": "asked_cmax", "value": None, "reason": "missing"}])

    def test_unparsable_invalidates_everything(self):
        for text in ("", "I think the route is oral", '{"route": "oral"', "[1, 2]"):
            a, bad = B.parse(text, QS)
            self.assertEqual(a, {}); self.assertEqual([b["question"] for b in bad], list(QS)); self.assertEqual({b["reason"] for b in bad}, {"unparsable"})


class DeciderTest(unittest.TestCase):
    def test_one_call_per_row(self):
        srv = FakeServer(echo_first_option)
        try:
            d = B.BonsaiDecider("row", url=srv.url, log=None)
            out = d(STATE, QS)
        finally: srv.close()
        self.assertEqual(out, {"route": "oral", "asked_cmax": "false"})
        self.assertEqual(len(srv.bodies), 1)
        b = srv.bodies[0]
        self.assertEqual(b["temperature"], 0)
        self.assertEqual(b["chat_template_kwargs"], {"enable_thinking": False})
        self.assertEqual(b["response_format"]["type"], "json_schema")
        self.assertEqual(set(b["response_format"]["json_schema"]["schema"]["properties"]), set(QS))
        self.assertEqual(d.stats["calls"], 1); self.assertEqual(d.stats["invalid"], 0); self.assertEqual(d.name, "bonsai-27b-row")

    def test_one_call_per_question(self):
        srv = FakeServer(echo_first_option)
        try:
            d = B.BonsaiDecider("question", url=srv.url, log=None)
            out = d(STATE, QS)
        finally: srv.close()
        self.assertEqual(out, {"route": "oral", "asked_cmax": "false"})
        self.assertEqual([list(b["response_format"]["json_schema"]["schema"]["properties"]) for b in srv.bodies], [["route"], ["asked_cmax"]])
        self.assertEqual(d.stats["calls"], 2); self.assertEqual(d.name, "bonsai-27b-question")

    def test_invalid_answers_are_counted_and_go_out_of_options(self):
        import harness as H
        srv = FakeServer('{"route": "by mouth", "asked_cmax": "true"}')
        try:
            d = B.BonsaiDecider("row", url=srv.url, log=None)
            out = d(STATE, QS)
        finally: srv.close()
        self.assertEqual(d.stats["invalid"], 1); self.assertEqual(d.invalid[0]["question"], "route"); self.assertEqual(d.invalid[0]["request"], "et la t1/2 ?")
        labels, outside = H.normalize_answers(out, QS)                  # what decision/eval_ood.py does with the answers
        self.assertEqual(outside, ["route"]); self.assertEqual(labels["asked_cmax"], "true")
        self.assertEqual(d.summary()["invalid_answers"], 1)

    def test_raw_output_is_logged(self):
        srv = FakeServer(echo_first_option)
        with tempfile.TemporaryDirectory() as tmp:
            log = os.path.join(tmp, "raw", "calls.jsonl")
            try: B.BonsaiDecider("row", url=srv.url, log=log)(STATE, QS)
            finally: srv.close()
            with open(log, encoding="utf-8") as f: rec = [json.loads(l) for l in f]
        self.assertEqual(len(rec), 1)
        self.assertEqual(json.loads(rec[0]["raw"]), {"route": "oral", "asked_cmax": "false"})
        self.assertEqual((rec[0]["mode"], rec[0]["finish_reason"], rec[0]["usage"]["prompt_tokens"]), ("row", "stop", 100))

    def test_dead_server_raises(self):
        with self.assertRaises(RuntimeError): B.BonsaiDecider("row", url="http://127.0.0.1:9", log=None)(STATE, QS)

    def test_module_level_deciders_are_named(self):
        self.assertEqual(B.decide.name, "bonsai-27b-row"); self.assertEqual(B.decide_per_question.name, "bonsai-27b-question")


if __name__ == "__main__":
    unittest.main()
