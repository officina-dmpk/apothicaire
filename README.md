# Apothicaire v0

**Hallucination count (numbers not found in a tool result or in a user message, over the numbers checked, by the deterministic gate `gate.py`): run 3 (2026-10-09, gate in the loop) 0/39 in the answers shown (7/48 in the first drafts, before the gate's one regeneration); run 1 (2026-10-08) 6/44 and run 2 (2026-10-08) 17/73, both re-scored with the gate on the stored transcripts, no gate in the loop.** One scripted conversation per run, one sampling seed: these are counts, not rates with an interval. Tool-call validity and numeric truthfulness are two different metrics; this README reports both and puts the second first.

## Benchmark

**25 synthetic exercises x 8 French turns = 200 turns (2026-10-09, Bonsai 2 27B, temperature 0.3, one run, gate in the loop).** Ground truth is simulated by Caladrius (`model_simulate`, proportional noise 5-10 %, fixed seed; pk1 IV bolus / infusion / oral with and without lag / zero-order and pk2 IV bolus / oral; doses in mg and ug, concentrations in ng/mL and mg/L, times in h and min; two BLQ exercises) and the oracle for the NCA questions is Caladrius `nca_run` on the written CSV. Full report: `bench/runs/2026-10-09/report.md` (+ `report.json`, one JSON per exercise).

| metric | result |
|---|---|
| **hallucination rate, first drafts** (numbers not in a tool result or user message / numbers checked) | **76 / 932 = 8.2 %** (95 % CI with exercises resampled 7.1-9.1 %) |
| **hallucination rate, answers shown** (after the gate's one regeneration) | **0 / 827 = 0 %** (rule of three: upper 95 % bound 0.36 %); the regeneration fixed 25 of 25 affected turns, no badge shown |
| where they are | all 76 in the `compare` turn (76 / 168 numbers there, 25 of 25 exercises); **0 / 764 in the seven other question types** |
| failure taxonomy (76, heuristic classes) | arithmetic 58 (differences, percentages and ratios of the two AUC), other 16, unit conversion 1, unlabelled misread 1, recall error 0 |
| turns fully correct (expected numbers present, none of the converted / computed values, expected words) | **193 / 200** (92 % compare, 92 % first turn, 96 % CL/Vz, t1/2 and recall, 100 % Cmax/Tmax, lambda_z and "not available"); expected numbers found 496 / 508 |
| tool calls | 112 valid, 2 invalid, 0 failed of 114 (98.2 %); 50 `nca_run` calls, all with the right dose and route |
| time | 10.1 s per turn on average (64 min for the 200 turns), 4 289 prompt tokens on the first call of a turn |

What the 7 incorrect turns are (the gate cannot see them: the numbers are in the tool results): ex13 (BLQ, oral) quotes `aucall` (to the last BLQ sample, 3152.57) as AUC(0-tlast) in turn 1 and again in turn 7 (the oracle's `auclast` is 2859.302, last quantifiable point); ex07 (BLQ, IV bolus) passes `start: zero` on its own, so every AUC differs from the oracle's (4 turns); ex21 says in the recall turn that the dose had no unit (it was 5000 ug). The 2 invalid calls: a column name with its unit (`time (min)`) in `data_import`, and `analysis_get` with a worksheet id.

Reading, and its limits:
- With the prompt change of 2026-10-09 ("quote tool values verbatim, never convert units; if a unit is missing, say so") the model no longer converts CL/F and Vz/F: 1 unit conversion in 932 numbers, against 10 occurrences in 73 in run 2 (different script, so only indicative). What it still does, in every exercise, is the arithmetic it is tempted to do when asked for a difference and a percentage between two AUC; the gate catches all of it, and one regeneration removes it each time (25 / 25). This is one run with one sampling: the 25 / 25 is a count, not a guarantee.
- The gate checks numbers, not claims. The 7 wrong turns above are right numbers on the wrong parameter, a wrong option, or a wrong recall: they need the oracle, which is what the correctness column is for.
- The taxonomy rules are heuristics (`bench/score.py`) and fire by chance on random numbers (about 11 % unit conversion and 11 % misread on random 3-digit numbers, 22 % arithmetic on random 4-digit numbers; the report prints this baseline). The unverified counts never depend on them.
- Single-subject synthetic data, one model, scripted questions (the `compare` turn is built to tempt arithmetic), exercises not shuffled. The scripts and rules were fixed before the run, but three things were changed after seeing results, all in the harness and listed here: (1) a preliminary run of the first 8 exercises (`bench/runs/2026-10-09-prelim-route-anyof/`) showed the 27B writing the infusion route object as a string (6 invalid `nca_run` calls, then a loop on exercise 5), so the schema was changed to `route = iv_infusion` + `infusion_duration` (the client builds the object) and all 25 exercises were rerun; (2) the taxonomy got an arithmetic rule on the numbers written in the same answer before that rerun; (3) after the run, the "says it is not available" patterns were widened because two valid answers ("ne retourne pas", "ne renvoie pas") were rejected, and the 200 turns were re-scored with `run_bench.py --rescore` (2 turns changed, nothing else).
- Not measured: fitting questions (the ground-truth simulation parameters are stored in each `meta.json` for them), longer conversations, other models.

The first working version of Apothicaire, the DMPK agent of Officina: **Bonsai 2 27B** (local llama.cpp, PrismML fork) + the **OptChat** endless-chat memory (`../optchat/optchat.py`, imported unchanged) + the **Caladrius** engine reached as MCP tools (`caladrius-mcp` over stdio). The model never computes pharmacokinetic numbers: it imports the data, calls Caladrius, and explains the results. Everything runs on the local RTX 3060. Since 2026-10-09 every final answer goes through a deterministic number gate (below).

## Files

| file | role |
|---|---|
| `apothicaire.py` | the agent: a small MCP stdio client (JSON-RPC 2.0 lines: `initialize`, `tools/list`, `tools/call`), conversion of the MCP tool schemas to OpenAI function definitions, the digest of NCA results, `Apothicaire(optchat.Agent)` which adds the Caladrius tools next to `zoom` / `read_message`, the system prompt addition, and the gate wiring |
| `gate.py` | the number gate: pure Python, no model. Its definitions (extraction, allowed set, matching rule, exemptions) are the module docstring |
| `run_exo1.py` | the scripted 4-turn French demo on exercise 1 (TD1, 10 mg oral); reports `numbers_unverified / numbers_total` per turn and in total |
| `tests/` | `test_digest.py` (golden files + schema flattening), `test_gate.py`, `test_agent_gate.py` (gate wiring with a scripted model and the real MCP server), `make_golden.py` (regenerates the goldens by hand), `golden/*.json` |
| `runs/` | transcripts (`<date>-exo1*.md`, `.json`) and the chat memory of each run (`<date>-exo1*-data/`). The exercise data is private coursework: it is read at run time and appears only here; **`runs/` is git-ignored** (the transcripts embed the CSV) |
| `bench/` | the benchmark: `make_exercises.py` (25 synthetic exercises simulated by Caladrius, `bench/exercises/<id>/data.csv` + `meta.json` with the oracle NCA), `scripts.py` (8 French turns per exercise type and the expected-answer rule of each), `score.py` (expected-number matching with the gate's rounding rule, failure taxonomy), `run_bench.py` (runner and report), `runs/<date>/` (per-exercise records, `report.json`, `report.md`; the `*-data/` memory folders are git-ignored) |
| `data/` | the chat memory of `apothicaire.py chat` / `say` (git-ignored); `gate.jsonl` there logs the gate's counts and findings of every turn |

## Run

```bash
# 1. the engine (once; absolute target dir)
cd ../caladrius && CARGO_TARGET_DIR=C:/Users/abdou/apothicaire/caladrius/target/agent-apothicaire cargo build --release -p caladrius-mcp
# 2. the model server (Bonsai 2 27B, 2 slots of 12k tokens, http://127.0.0.1:18435; ~15 s)
bash ../optchat/start_servers.sh && curl http://127.0.0.1:18435/health
# 3. the agent
python apothicaire.py chat            # interactive, memory in data/
python apothicaire.py tools           # exposed tools and static prompt size
python run_exo1.py                    # the demo -> runs/<date>-exo1.md
# 4. stop the server (PowerShell; taskkill does nothing under Git Bash)
powershell -Command "Stop-Process -Name llama-server -Force"
# the benchmark (model server needed; ~3 min per exercise)
python bench/make_exercises.py        # regenerates bench/exercises/ (deterministic; needs the built caladrius-mcp)
python bench/run_bench.py --date 2026-10-09 [--first 10] [--resume]   # -> bench/runs/<date>/report.md
# tests (no model server needed; test_agent_gate.py needs the built caladrius-mcp and is skipped without it)
python -m unittest discover -s tests
```

Environment: `APOTHICAIRE_MCP` (path of the `caladrius-mcp` binary, default `../caladrius/target/agent-apothicaire/release/caladrius-mcp.exe`), `APOTHICAIRE_DATA` (memory folder), `OPTCHAT_URL`. Python 3.12 + httpx only. Tests use `unittest` (pytest is not installed).

## Pinned versions (what the numbers below were measured with)

- **llama.cpp**: the PrismML fork, CUDA build, `C:\Users\abdou\mitsuba\llama\llama-server.exe`; `llama-server --version` prints `version: 0.2.0-dev (build 10743, commit adfffbe41)`, built with MSVC 19.44.35229.0 for Windows AMD64.
- **Model**: `Ternary-Bonsai-2-27B-PTQ1_0.gguf` (file name as on disk; format `PTQ1_0`), 5 946 648 928 bytes, SHA-256 `53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3`.
- **Server flags** (`../optchat/start_servers.sh`): `-c 24576 -np 2 -ngl 99 --jinja -fa on -ctk q8_0 -ctv q8_0 --slots --metrics` (2 slots of 12 288 tokens; slot 0 chat, slot 1 compaction). Sampling: temperature 0.3, no fixed seed, so two runs of the same script differ.
- **Engine**: `caladrius-mcp` 0.1.0, 20 tools listed; the golden files were frozen from Caladrius commit `f4bcacd04b28` (`tests/golden/*.json` store it).

## The number gate

Rule: every number the assistant writes must already be in a tool result (Caladrius) or in a user message (the CSV included). After each final answer `gate.check` extracts the numbers (French and English decimal marks, thousands separators, scientific notation, percentages, units attached) and looks each one up in that set; a number matches an allowed number when the allowed number, rounded to the significant digits written in the answer (at least 2), equals it. So `6,98 %` matches 6.98412 and `7,0 %` too, `6,99 %` does not. **Unit conversions and values computed by the model (differences, ratios, percent changes) are not allowed.** Exempt, not counted: integers 0 to 20 with no unit (counts), years, ISO dates, numbers after a step/label word or a list marker, `#17` message references, bare `10^k`. The assistant's earlier answers and the results of `zoom` / `read_message` are not sources.

In the agent (`Apothicaire._chat_call`): on findings, one regeneration with a `[system reminder]` message appended at the end of the messages (system prompt and tool definitions are untouched, so the cached prefix is intact; it is a `user` role message because chat templates reject a late `system` message) listing the offending numbers and the rule "quote tool values verbatim, never convert"; the better of the two answers is kept; if findings remain, `⚠ n number(s) not found in tool results: ...` is appended to what the user sees. The memory stores the answer without badge or reminder. The turn's stats carry `gate`: counts before and after the regeneration, the findings (number, position, nearest allowed value, power-of-ten hint), the first draft; `run_exo1.py` writes them to the transcript JSON.

Metric: `numbers_unverified / numbers_total`, where `numbers_total` counts the checked numbers (exempt ones excluded), per turn and in total, before the regeneration and in the answer shown.

Known limits, stated plainly:
- The gate is conservative in one direction only. A computed number with 2 or 3 significant digits can coincide with some tool number after rounding (a `−1.00 %` change passed because the tool also contains `1.00`); the counts are a lower bound. A hand review of the transcripts stays part of the protocol.
- It checks numbers, not claims: a right number attached to the wrong parameter or the wrong unit passes (units are read for the exemption rule, not compared with the tool's unit).
- A value the user typed in another format than the tool's is allowed in every plausible reading (`1,234` is 1.234 and 1234).

## Tests

104 `unittest` tests, `python -m unittest discover -s tests`, about 5-15 s (the agent tests start the real `caladrius-mcp`).

- `test_digest.py` (23): five frozen `nca_run` answers on PUBLIC data only (theoph subject 1 oral with the dose as an argument and explicit units; indometh IV bolus; edge_blq 6 subjects with BLQ removals and flags; edge_iv with a `no_rise` reason; edge_negative with per-subject errors), each next to the exact tool arguments, and the `tools/list` answer. They assert that `digest_analysis` reproduces every computed parameter as "value unit" at 6 significant digits with an independently written unit table, percentages as `%`, the not-calculated parameters with their reason, λz regression, options, flags, removed points, errors, and that **no number of the digest is absent from the payload**; plus a test that the detector fails when a value is converted or invented, and tests of `_inline` / `to_openai` on the stored schemas. Mutating the rounding or the percent rule in the digest makes 27 and 12 subtests fail.
- `test_gate.py` (42): formats, rounding rule, exemptions, sources, and synthetic sentences built from public golden numbers that reproduce the run-2 hallucinations (CL/F and Vz/F times the dose, times 10^3; six converted values in one answer) and computed differences/percents; the transcripts themselves are not used in any test.
- `test_agent_gate.py` (8): the wiring with a scripted model and the real server: regeneration with the reminder at the end of the messages and nothing before it changed, clean answer = no extra call, badge after a failed regeneration, a worse regeneration not kept, error during regeneration, the memory holding no badge or reminder, the sources of the gate.
- `test_nca_route.py` (3): the infusion route (`iv_infusion` + `infusion_duration` becomes the server's route object; a stringified object is parsed; a missing duration is an error text for the model; the real server accepts the result).
- `test_bench_exercises.py` (6): the plan (25 exercises: models, units, BLQ, minutes), the generator is deterministic (two runs byte-identical, equal to the committed CSV and simulation parameters), every committed exercise round-trips through `data_import` + `nca_run` and reproduces the stored oracle values exactly.
- `test_bench_score.py` (13): the scorer (expected numbers with the gate's rounding rule, forbidden values at 3+ digits, words, "not available") and the failure taxonomy on synthetic answers, including the chance baseline of the rules.
- `test_bench_run.py` (9): the 8-turn scripts for all 25 exercises (the truth answer scores correct on every turn, converted / computed answers do not, the "not available" phrasings), `classify_call`, the report arithmetic on synthetic records, and one exercise run end to end with a scripted model and the real server (a conversion in a first draft, fixed by the regeneration).

Goldens are regenerated by hand with `python tests/make_golden.py` after a deliberate engine change; review the diff. Coursework data never goes into a test or golden file.

## Design choices

- **Tools exposed**: `zoom`, `read_message` (memory) + `data_import`, `nca_run`, `analysis_get`, `export_table`. The 20 Caladrius tools do not fit a 12k context; `fit_run` alone is ~3 kB of schema, so fitting is left out of v0. Schemas are flattened (`$ref` inlined) and `nca_run` shows only the options `auc_method`, `start`, `lambda_z`, `quality` (the server still accepts all of them). The route is `extravascular`, `iv_bolus` or `iv_infusion` plus a number `infusion_duration`; the client builds the server's `{"iv_infusion": {"duration": d}}` (the 27B wrote that object as a string when the schema offered it as an `anyOf`: tool-call validity, found by the benchmark). **Static prefix: 2 229 tokens** (system prompt + 6 tools; was 2 154 before the 2026-10-09 prompt change and the infusion route of `nca_run`), under the 2.5k budget, cached by llama.cpp.
- **NCA results are digested for the model**: a raw `nca_run` answer is ~17 kB of pretty JSON (7 kB compact: every λz candidate, the profile, ~60 parameters). The client gives the model the same values reorganised: each computed parameter as `"value unit"` (6 significant digits; units labelled from the worksheet column units, `aucpext.*` as %), the names of the parameters not calculated with the reason, the selected λz regression, the options used (auc_method, lambda_z, quality thresholds, BLQ, missing, negative, start), the flags and the engine's `flag_messages`, the `not_calculated_messages` (grouped by identical text) and the worksheet's `unit_warnings` (e.g. `mass_mismatch`, `missing_unit`). No value is converted. The full answer is kept in the tool log and the transcript. Since 2026-10-09 (after the golden tests found them missing) the digest also carries the BLQ / missing / negative / start options, `flag_messages`, `not_calculated_messages` and `unit_warnings`.
- `data_import` also accepts `path` instead of `csv` (the client reads the file); in the demo the CSV is put in the user message by Python and the model copies it into `csv`.
- The digest goes through OptChat unchanged: tool calls and results are logged, summarised and zoomable like any message.

## Demo results (exercise 1, 4 turns in French)

Run 1 and run 2 (2026-10-08) had no gate; run 3 (2026-10-09) is the same script with the gate in the loop (same system prompt, same model, same sampling); the first one revealed a unit problem, fixed in the client before the second. Their hallucination rows were first counted by hand (1 and 6) and are re-scored here by the gate on the stored transcripts, counting every occurrence of a number.

| | run 1 | run 2 | run 3 (gate) |
|---|---|---|---|
| **numbers not found in a tool result or user message / numbers checked (gate re-score)** | **6 / 44** | **17 / 73** | **7 / 48 in the first drafts (4/20, 3/24, 0/4, 0/0 per turn), 0 / 39 shown (0/17, 0/18, 0/4, 0/0)** |
| of which | 3 occurrences of one wrong recomputation of the % extrapolated (off by a factor ~45) + 3 occurrences of differences computed by the model (right values) | 10 occurrences of unit conversions of CL/F and Vz/F (6 distinct wrong values: multiplied by the dose and by 10^3), 7 occurrences of differences / percent changes computed by the model | turn 1: 4 conversions of CL/F and Vz/F (x10, x10^4) written in the first draft; turn 2: 3 computed differences / percent changes. The regeneration (told to quote verbatim and never convert) removed all of them: the shown answers keep `dose unit/(...)` and say Caladrius returned no difference |
| hand count (v0 for runs 1-2; run 3: hand review of the first drafts) | 1 | 6 | 9 in the first drafts (the gate missed `−1.00 %` and `−1.0 %`, computed changes that coincide with the tool value 1.00); 0 found in the shown answers |
| MCP calls (tool-call validity) | 5, all valid and successful | 3, all valid and successful | 5, 4 successful (turn 4: `analysis_get` with a worksheet id, `unknown_analysis`; the model then recalled the dose with `zoom`) |
| CSV copied into `data_import` | identical to the file | identical | identical |
| wall time per turn (s) | 36.4 / 20.9 / 10.8 / 10.6 | 36.9 / 30.4 / 6.5 / 2.7 | 54.0 / 51.1 / 7.2 / 9.4 (a regeneration adds 17-21 s on turns 1 and 2) |
| prompt tokens, first call of each turn | 2 382 / 4 268 / 5 684 / 4 527 | 2 386 / 4 455 / 6 216 / 6 400 | 2 386 / 4 350 / 5 974 / 4 349 (static prefix 2 154, unchanged) |
| Caladrius values quoted faithfully | yes, but `aucpext.obs` (a %) presented as an AUC in h·ng/mL | yes, all | yes, all, units as returned (`dose unit/...`) |
| memory recall (turn 4: dose and method of turn 1) | right method and dose value, via `analysis_get` after compaction; says the dose unit was not given (it was) | right (10 mg, linear), from the raw messages still in view | right (dose 10 mg, linear) |

Reading: run 2 was better than run 1 on tool-call validity (3 calls instead of 5, all valid) and **worse on numeric truthfulness (6 distinct wrong values against 1)**: the unit labelling fix in the client moved the problem, from a misread percentage to unit conversions of CL/F and V, it did not remove it. v0 called run 2 "final" on the first metric only; that was the wrong summary. The digest labels units but cannot stop the model from converting them; only the gate can catch it.

Run 3 in one line: with the gate, the 27B still writes the conversions and the computed differences in its first draft (the gate does not stop the model from producing them), and the single regeneration removed them in both affected turns. This is one run: it shows that the loop works, not that the regeneration always succeeds (the code handles the case where it does not: badge, and the better of the two answers is kept). The price is latency (+17 to +21 s on the two affected turns) and the gate's blind spot on low-precision numbers (see above).

Turn 1 costs three LLM rounds (import, NCA, answer) and a long answer at ~24 tok/s; follow-up questions answered from the context take 3 to 7 s. Generation dominates; prompt evaluation stays cheap thanks to the cached static prefix.

## Problems found

1. **Unit conversion by the model is the main hallucination source.** Caladrius only knows the dose unit from a dose column, so with a dose given as an argument CL and V come in `dose unit/(...)` and the 27B converts by itself, wrongly. Fix on the engine side (suggested): a `dose_unit` parameter for `nca_run` (and the fits) so that Caladrius reports CL in L/h and V in L. The system prompt used to say "if you convert them, show the factor", which invited the conversion the gate then has to catch; since 2026-10-09 it says "quote tool values verbatim and never convert units; if a unit is missing, say so" (runs 1-3 above were made with the old wording).
2. **Unlabelled numbers get misread**: without per-parameter units the model took a percentage for an AUC (run 1). Labelling every parameter with its unit in the digest fixed it. Caladrius could return the unit of each parameter itself.
3. The model still does arithmetic itself (differences, percent changes), right or wrong; the gate reports it. A `compare` command (two analyses, differences and ratios) would remove the temptation.
4. Turn 4 of run 2 did not exercise the summary memory (compaction only triggers above 12 raw messages); run 1 did, and the model used Caladrius's own project state (`analysis_get`) rather than `zoom` to recall turn 1, which is a good habit.
5. The old number checker of `run_exo1.py` (a relative tolerance let one wrong value match by accident) is replaced by the gate; the transcripts still end with a hand review.
