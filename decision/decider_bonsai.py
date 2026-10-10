"""Control decider of D-01: the generic local 27B (Bonsai 2 27B, llama.cpp server) answers the same closed questions as the trained 0.8B.

  python decision/eval_ood.py --decider decision.decider_bonsai:decide --no-run             # one call per row, all questions at once
  python decision/eval_ood.py --decider decision.decider_bonsai:decide_per_question --no-run # one call per question

`decide(state, questions) -> {question: label}` as decision/eval_ood.py and decision/harness.py expect it. The server is the one of
../optchat/start_servers.sh (OpenAI-style /v1/chat/completions on $BONSAI_URL, default http://127.0.0.1:18435). Temperature 0, thinking off,
no chain of thought: the answer is a JSON object whose values are constrained, by the server's grammar (`response_format` json_schema), to the
offered options of each question. The parser is strict anyway: a value outside the options, a missing key or an unparsable output is recorded
as invalid (never silently repaired) and handed to the caller as an out-of-options answer, which the scorer counts as wrong.

The 27B sees exactly what the 0.8B sees: the state JSON and, per question, its instructions and the description of each option.

Environment: BONSAI_URL (server), BONSAI_LOG (JSONL file of every call with its raw output; `<log>.summary.json` is written at exit),
BONSAI_TIMEOUT (seconds, default 600).
"""
import atexit, json, os, re, subprocess, time, urllib.error, urllib.request

URL = os.environ.get("BONSAI_URL", "http://127.0.0.1:18435")
TIMEOUT = float(os.environ.get("BONSAI_TIMEOUT", "600"))
MODEL = "bonsai"

SYSTEM = """You are a classifier inside a pharmacokinetics assistant. You read the state of a conversation and answer closed questions about the user's last request.

The state is a JSON object:
- "request": the last message of the user (usually French).
- "user_dose_sentence": the sentence in which the user gave the dose, the route or the units (it may be the same text as the request).
- "data": the concentration table the user pasted: its header, its number of rows and subjects, its first rows.
- "notes": remarks the user made about the data.
- "analyses": the analyses already run in the project (id, kind, AUC method); an empty list means nothing has been run yet.

Answer only from the state. Reply with one JSON object and nothing else: no explanation, no reasoning. Each value must be exactly one of the offered option names."""


def state_text(state):
    return json.dumps(state, ensure_ascii=False, sort_keys=True, indent=1)


def options_of(spec):
    """Offered option names of a question, in the order of its criteria ('true'/'false' for a noul question)."""
    return list(spec["criteria"]) if spec["type"] == "choice" else ["false", "true"]


def question_block(name, spec):
    lines = [f'Question "{name}": {spec["instructions"]}']
    for opt in options_of(spec):
        lines.append(f'  - {opt}: {spec["criteria"].get(opt, "")}')
    return "\n".join(lines)


def schema_of(questions):
    """JSON schema of the answer object: one required key per question, its value one of the options."""
    return {"type": "object", "additionalProperties": False, "required": list(questions),
            "properties": {q: {"type": "string", "enum": options_of(s)} for q, s in questions.items()}}


def build_messages(state, questions):
    """Chat messages of one call. The state comes first, the questions last (the llama.cpp prompt cache then shares the state prefix between
    the per-question calls of a row)."""
    names = list(questions)
    ask = ("Answer the question below." if len(names) == 1 else f"Answer all {len(names)} questions below.")
    user = ("State:\n" + state_text(state) + "\n\n" + ask + " Reply with one JSON object with the key"
            + ("s " + ", ".join(f'"{n}"' for n in names) if len(names) > 1 else f' "{names[0]}"') + ".\n\n"
            + "\n\n".join(question_block(n, s) for n, s in questions.items()))
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def parse(content, questions):
    """(answers, invalid) from the raw text of a reply. answers: {question: option}; a question whose value is missing or outside its options
    is absent from answers and listed in invalid as {"question", "value", "reason"}. Unparsable text invalidates every question."""
    bad = lambda why, v=None: [{"question": q, "value": v, "reason": why} for q in questions]
    text = (content or "").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    try:
        obj = json.loads(text)
    except ValueError:
        m = re.search(r"\{.*\}", text, re.S)                        # an object buried in other text
        try: obj = json.loads(m.group(0)) if m else None
        except ValueError: obj = None
    if not isinstance(obj, dict): return {}, bad("unparsable", text[:200])
    answers, invalid = {}, []
    for q, spec in questions.items():
        if q not in obj: invalid.append({"question": q, "value": None, "reason": "missing"}); continue
        v = obj[q]
        if isinstance(v, bool): v = "true" if v else "false"       # a noul answer given as a JSON boolean is the same answer
        if isinstance(v, str) and v in options_of(spec): answers[q] = v
        else: invalid.append({"question": q, "value": v, "reason": "outside options"})
    return answers, invalid


def call(messages, schema, max_tokens, url=None):
    """One chat completion at temperature 0; (content, finish_reason, usage, seconds). Raises on transport errors (a dead server must stop the run)."""
    body = {"model": MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": 0, "cache_prompt": True,
            "chat_template_kwargs": {"enable_thinking": False},
            "response_format": {"type": "json_schema", "json_schema": {"name": "answers", "strict": True, "schema": schema}}}
    req = urllib.request.Request((url or URL) + "/v1/chat/completions", json.dumps(body).encode("utf-8"), {"Content-Type": "application/json"})
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r: d = json.load(r)
    except urllib.error.URLError as e:
        raise RuntimeError(f"model server unreachable at {url or URL}: {e}") from e
    ch = d["choices"][0]
    return ch["message"].get("content") or "", ch.get("finish_reason"), d.get("usage") or {}, time.perf_counter() - t0


class BonsaiDecider:
    """mode "row": one call per row (all questions at once); mode "question": one call per question."""
    def __init__(self, mode="row", url=None, log=None):
        assert mode in ("row", "question")
        self.mode, self.url = mode, url
        self.name = {"row": "bonsai-27b-row", "question": "bonsai-27b-question"}[mode]
        self.log = log if log is not None else os.environ.get("BONSAI_LOG")
        self.stats = {"rows": 0, "calls": 0, "seconds": 0.0, "decisions": 0, "invalid": 0, "prompt_tokens": 0, "completion_tokens": 0}
        self.invalid = []

    def _ask(self, state, questions):
        text, why, usage, dt = call(build_messages(state, questions), schema_of(questions), 60 * len(questions) + 60, self.url)
        answers, invalid = parse(text, questions)
        if why == "length" and invalid and not answers: invalid = [dict(i, reason="cut by max_tokens") for i in invalid]
        self.stats["calls"] += 1; self.stats["seconds"] += dt
        self.stats["prompt_tokens"] += usage.get("prompt_tokens") or 0; self.stats["completion_tokens"] += usage.get("completion_tokens") or 0
        if self.log:
            os.makedirs(os.path.dirname(os.path.abspath(self.log)), exist_ok=True)
            with open(self.log, "a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps({"mode": self.mode, "request": state.get("request"), "questions": list(questions), "raw": text,
                                    "finish_reason": why, "seconds": round(dt, 3), "usage": usage, "invalid": invalid}, ensure_ascii=False) + "\n")
        return answers, invalid

    def __call__(self, state, questions):
        groups = [questions] if self.mode == "row" else [{q: s} for q, s in questions.items()]
        out, bad = {}, []
        for g in groups:
            a, i = self._ask(state, g)
            out.update(a); bad += i
        self.stats["rows"] += 1; self.stats["decisions"] += len(questions); self.stats["invalid"] += len(bad)
        self.invalid += [dict(b, request=state.get("request")) for b in bad]
        for b in bad: out[b["question"]] = b["value"] if isinstance(b["value"], str) else None      # out-of-options: counted wrong, not repaired
        return out

    def summary(self):
        s, n = self.stats, max(1, self.stats["rows"])
        out = {"model": "Ternary-Bonsai-2-27B-PTQ1_0 (llama-server, %s)" % (self.url or URL), "mode": self.mode, "rows": s["rows"], "calls": s["calls"],
               "decisions": s["decisions"], "invalid_answers": s["invalid"], "seconds_total": round(s["seconds"], 1),
               "seconds_per_row": round(s["seconds"] / n, 2), "prompt_tokens": s["prompt_tokens"], "completion_tokens": s["completion_tokens"]}
        try:
            used = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=20)
            out["nvidia_smi_used_mib"] = int(used.stdout.strip().splitlines()[0])
        except Exception:
            pass
        return out


def _make(mode):
    d = BonsaiDecider(mode)
    if d.log:
        def dump():
            if d.stats["rows"]:
                with open(d.log + ".summary.json", "w", encoding="utf-8", newline="\n") as f:
                    json.dump({**d.summary(), "invalid": d.invalid}, f, ensure_ascii=False, indent=1)
        atexit.register(dump)
    return d


_DECIDERS = {}


def _get(mode):
    if mode not in _DECIDERS: _DECIDERS[mode] = _make(mode)
    return _DECIDERS[mode]


def decide(state, questions):
    """One call per row, all questions at once."""
    return _get("row")(state, questions)
decide.name = "bonsai-27b-row"
decide.summary = lambda: _get("row").summary()


def decide_per_question(state, questions):
    """One call per question."""
    return _get("question")(state, questions)
decide_per_question.name = "bonsai-27b-question"
decide_per_question.summary = lambda: _get("question").summary()
