"""Tests of the decision-model dataset (decision/make_dataset.py): the typed-decisions row schema, gold answers inside the declared
options and consistent with the truth of the exercises (checked from meta.json and the dose sentence, not from the generator's own
tables), the split by exercise, the class balance printed in decision/README.md, determinism. No engine and no model needed, except
for the optional byte-identity check of decision/exercises/ (skipped when caladrius-mcp is not built).
"""
import collections, filecmp, json, os, re, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
sys.path.insert(0, AGENT); sys.path.insert(0, os.path.join(AGENT, "decision"))
import apothicaire  # noqa: E402
import make_dataset as md  # noqa: E402
from bench import make_exercises as mk, scripts  # noqa: E402

FIELDS = ["id", "workflow", "split", "state", "questions", "gold", "factors", "label_agreement", "n_questions"]
TYPES = {"choice", "noul", "score"}

_CACHE = {}
def data():
    if "data" not in _CACHE: _CACHE["data"] = md.build()
    return _CACHE["data"]

def metas():
    if "metas" not in _CACHE: _CACHE["metas"] = {m["id"]: m for m, _, _ in md.load_exercises()}
    return _CACHE["metas"]

def parsed(rows):
    for r in rows:
        yield r, json.loads(r["state"]), json.loads(r["questions"]), json.loads(r["gold"]), json.loads(r["factors"])

def options_of(q):
    """The declared answers of a question."""
    if q["type"] == "choice": return set(q["criteria"])
    if q["type"] == "noul": return {"false", "true"}
    return {str(i) for i in range(len(q["criteria"]))}

class TestDecisionDataset(unittest.TestCase):
    def test_row_schema(self):
        for rows in data():
            ids = set()
            for r, state, qs, gold, factors in parsed(rows):
                assert list(r) == FIELDS
                assert all(isinstance(r[k], str) for k in FIELDS if k != "n_questions") and isinstance(r["n_questions"], int)
                assert r["id"] not in ids; ids.add(r["id"])
                assert r["split"] in ("train", "test", "bench") and r["id"].startswith({"train": "tr_", "test": "te_", "bench": "be_"}[r["split"]])
                assert r["n_questions"] == len(qs) == len(gold) == 6 + len(md.PARAMETERS) and set(qs) == set(gold) == set(json.loads(r["label_agreement"]))
                assert set(state) == {"analyses", "data", "notes", "request", "user_dose_sentence"}
                assert set(state["data"]) == {"header", "first_rows", "n_rows", "n_subjects"}
                assert state["data"]["header"].startswith("time (") and "conc (" in state["data"]["header"]
                assert state["data"]["n_rows"] >= len(state["data"]["first_rows"]) > 0
                assert state["request"].strip() and state["user_dose_sentence"].strip()
                for name, q in qs.items():
                    assert q["type"] in TYPES and isinstance(q["instructions"], str) and q["instructions"]
                    if q["type"] == "choice": assert len(q["criteria"]) >= 2 and all(isinstance(v, str) for v in q["criteria"].values())
                    if q["type"] == "noul": assert q["criteria"].keys() == {"false", "true"}
                    if q["type"] == "score": assert isinstance(q["criteria"], list) and len(q["criteria"]) >= 2
                    g = gold[name]
                    assert g["type"] == q["type"] and set(g["probabilities"]) == options_of(q)
                    assert abs(sum(g["probabilities"].values()) - 1) < 1e-9 and 0 <= g["confidence"] <= 1
                    if q["type"] == "noul": assert g["noul"] == g["probabilities"]["true"]
                assert set(json.loads(r["factors"])) >= {"exercise", "kind", "bench", "route"}

    def test_split_values_and_files_on_disk(self):
        for name, rows in zip(md.FILES, data()):
            path = os.path.join(md.OUT, f"{name}.jsonl")
            if not os.path.exists(path): continue                              # decision/data/ is git-ignored: checked when present
            with open(path, encoding="utf-8") as f: disk = [json.loads(l) for l in f]
            assert disk == rows, f"{path} is stale: run python decision/make_dataset.py"

    def test_deterministic(self):
        assert md.build() == data()

    # ---------------------------------------------------------------- gold answers
    def test_every_gold_is_a_declared_option(self):
        for rows in data():
            for r, state, qs, gold, factors in parsed(rows):
                for name, q in qs.items():
                    assert gold[name]["label"] in options_of(q), (r["id"], name, gold[name]["label"])
                    assert gold[name]["probabilities"][gold[name]["label"]] == 1.0
                ids = sorted(a["id"] for a in state["analyses"])
                pairs = {f"{a}+{b}" for a in ids for b in ids if a != b}                 # directed: both orders are offered
                assert set(qs["compare_pair"]["criteria"]) == {"not_applicable"} | (pairs or {"none_available"})

    def test_is_not_available_exactly_for_the_not_available_kind(self):
        n_true = 0
        for r, state, qs, gold, factors in parsed(sum(data(), [])):
            flag = gold["is_not_available"]["label"] == "true"
            assert flag == (factors["kind"] == "not_available"), r["id"]
            # independent of the kind table: the parameter asked is, or is not, among those Caladrius did not compute for this route
            asked = {p for p in factors["parameters_asked"] if p in ("c0", "tlag")}
            assert flag == bool(asked & set(metas()[factors["exercise"]]["ground_truth"]["nca"]["linear"]["not_calculated"])), r["id"]
            n_true += flag
        assert n_true > 0

    def test_gold_against_the_truth_of_the_exercise(self):
        for r, state, qs, gold, factors in parsed(sum(data(), [])):
            meta = metas()[factors["exercise"]]; kind = factors["kind"]; label = lambda q: gold[q]["label"]
            route = scripts.kind_of(meta)
            sentence = state["user_dose_sentence"]
            # route: what the sentence says, which must agree with meta.json
            says = [k for k, rx in md.ROUTE_RE.items() if re.search(rx, sentence)]
            assert says == ([] if label("route") == "unknown" else [route]), (r["id"], sentence)
            assert label("route") == ("unknown" if factors["route_omitted"] else route)
            assert label("dose_has_unit") == ("false" if re.search(md.UNIT_RE, sentence) is None else "true")
            assert (label("dose_has_unit") == "false") == factors["dose_unit_omitted"]
            assert str(meta["dose"]["amount"]).replace(".", ",") in sentence
            # analysis, AUC method, pair
            assert label("analysis") == {"import_nca": "nca", "compare": "compare", "fit_pk1": "fit_pk1", "fit_pk2": "fit_pk2",
                                         "simulate": "simulate"}.get(kind, "none_needed")
            assert label("auc_method") == {"import_nca": "linear", "compare": "lin_up_log_down"}.get(kind, "not_applicable")
            assert (label("compare_pair") != "not_applicable") == (kind == "compare")
            if kind == "compare": assert label("compare_pair") == "2+3"
            # parameters asked: one boolean `asked_<key>` per parameter, true exactly for the keys the wording names
            p = factors["parameters_asked"]
            assert [k for k in md.PARAMETERS if label(f"asked_{k}") == "true"] == [k for k in md.PARAMETERS if k in p], r["id"]
            if kind == "recall": assert p == []
            # the state's analyses
            assert state["data"]["header"] == f"time ({meta['units']['time']}),conc ({meta['units']['conc']})"
            assert (state["analyses"] == []) == (kind == "import_nca")
            assert bool(meta.get("blq")) == bool(state["notes"])

    def test_scripted_rows_are_the_benchmark_wording(self):
        n = 0
        for r, state, qs, gold, factors in parsed(sum(data(), [])):
            if not factors["scripted_wording"]: continue
            meta = metas()[factors["exercise"]]
            with open(os.path.join(md.BENCH_DIR if factors["bench"] else md.EXTRA_DIR, meta["id"], "data.csv"), encoding="utf-8") as f: csv = f.read()
            turns = {t["kind"]: t for t in scripts.build_script(meta, csv)}
            t1 = turns["import_nca"]["question"].split(chr(10))
            assert factors["kind"] in scripts.KINDS and state["user_dose_sentence"] == t1[0]
            assert state["request"] == (t1[-1] if factors["kind"] == "import_nca" else turns[factors["kind"]]["question"])
            n += 1
        assert n == 8 * 100

    def test_compare_pairs_are_directed(self):
        """2026-10-10 (review, defect 2): "compare analysis 3 to analysis 2" must be representable, so a pair is ordered (a = reference)."""
        crit = md.questions_for([2, 3])["compare_pair"]["criteria"]
        assert set(crit) == {"not_applicable", "2+3", "3+2"}
        assert "analysis 2 as the reference" in crit["2+3"] and "analysis 3 as the reference" in crit["3+2"]
        assert set(md.questions_for([2])["compare_pair"]["criteria"]) == {"not_applicable", "none_available"}
        assert len(md.questions_for([2, 3, 4])["compare_pair"]["criteria"]) == 1 + 6

    def test_not_supported_is_an_analysis_option_without_generated_rows(self):
        """2026-10-10 (review, defect 5): out-of-scope asks have their own answer; the generator writes no such request, so no row is
        relabelled (the labels are those of the dataset before the option existed)."""
        assert "not_supported" in md.questions_for([2])["analysis"]["criteria"]
        assert not any(json.loads(r["gold"])["analysis"]["label"] == "not_supported" for r in sum(data(), []))

    def test_one_noul_question_per_parameter(self):
        """`asked_<key>` replaces the single parameter_asked choice: one noul per parameter, a boolean gold, no several / none."""
        keys = ["cmax", "tmax", "c0", "auclast", "aucinf", "lambda_z", "half_life", "cl", "vz", "mrt", "aucpext", "lambda_z_points", "adj_r2", "tlag"]
        assert list(md.PARAMETERS) == keys
        qs = md.questions_for([2, 3])
        assert "parameter_asked" not in qs and [q for q in qs if q.startswith("asked_")] == [f"asked_{k}" for k in keys]
        for r, state, qs, gold, factors in parsed(sum(data(), [])):
            asked = []
            for k in keys:
                q, g = qs[f"asked_{k}"], gold[f"asked_{k}"]
                assert q["type"] == "noul" and q["criteria"] == md.TF and g["type"] == "noul"
                assert g["label"] in ("true", "false") and g["noul"] in (0.0, 1.0) and g["noul"] == (g["label"] == "true")
                if g["label"] == "true": asked.append(k)
            kind = factors["kind"]
            # every turn that expects numbers (the 6 reading kinds, the first request, the compare turn) asks at least one parameter
            if kind in ("import_nca", "cmax_tmax", "clearance_volume", "half_life", "lambda_z_regression", "compare", "nca_other"):
                assert asked, r["id"]
            # no parameter on a recall, a fit or a simulation
            if kind in ("recall", "fit_pk1", "fit_pk2", "simulate"): assert asked == [], r["id"]
            # the not-available turn asks the one parameter Caladrius did not compute for the route (C0 or Tlag), and no other
            not_calculated = set(metas()[factors["exercise"]]["ground_truth"]["nca"]["linear"]["not_calculated"])
            if kind == "not_available":
                assert len(asked) == 1 and asked[0] in ("c0", "tlag") and asked[0] in not_calculated, r["id"]
            else:
                assert not set(asked) & not_calculated, r["id"]          # no other turn asks for what the route does not give
            if kind == "import_nca" and factors["scripted_wording"]:
                assert asked == [k for k in keys if k in ("cmax", "tmax", "auclast", "aucinf", "lambda_z", "half_life", "cl", "vz", "mrt")]
            if kind == "compare": assert asked == ["auclast"]

    # ---------------------------------------------------------------- paraphrases
    def test_paraphrases_are_french_hand_written_and_several_per_kind(self):
        for key, pool in md.WORDINGS.items():
            assert len(pool) >= 3, key                                          # at least three wordings per turn kind
            texts = [t for t, _ in pool]
            assert len(set(texts)) == len(texts)
            for t, params in pool:
                assert re.search(r"[éèàêç']|\b(?:le|la|les|de|des|un|une|est|et|ou|moi|je|ai)\b", t), t
                assert all(p in md.PARAMETERS for p in params) and len(set(params)) == len(params), (key, params)
        assert set(scripts.KINDS + md.EXTRA_KINDS) == set(md.KINDS)

    def test_each_scripted_kind_has_distinct_rows_per_exercise(self):
        seen = collections.defaultdict(list)
        for r, state, qs, gold, factors in parsed(sum(data(), [])):
            seen[(factors["exercise"], factors["kind"])].append(state["request"])
        assert len(seen) == 100 * 12
        for key, requests in seen.items():
            assert len(requests) == 3 and len(set(requests)) == len(requests), key

    # ---------------------------------------------------------------- split by exercise
    def test_split_is_by_exercise(self):
        train, held, bench = data()
        ex = lambda rows: {f["exercise"] for *_, f in parsed(rows)}
        tr_ex, he_ex, be_ex = ex(train), ex(held), ex(bench)
        assert tr_ex and he_ex and be_ex and not (tr_ex & he_ex or tr_ex & be_ex or he_ex & be_ex)   # whole exercises, in one file only
        assert tr_ex | he_ex | be_ex == set(metas())
        bench_ids = {os.path.basename(d) for d in mk.list_exercises(md.BENCH_DIR)}
        new_ids = {os.path.basename(d) for d in mk.list_exercises(md.EXTRA_DIR)}
        assert be_ex == bench_ids and len(bench_ids) == 25                       # every benchmark exercise in bench.jsonl, none elsewhere
        assert not (tr_ex | he_ex) & bench_ids and tr_ex | he_ex == new_ids       # train and held-out come from the 75 new exercises
        assert len(he_ex) == md.HELDOUT_N == 20 and 0.2 <= len(he_ex) / len(new_ids) <= 0.3
        for rows, split in ((train, "train"), (held, "test"), (bench, "bench")):
            for r, state, qs, gold, f in parsed(rows):
                assert r["split"] == split and f["bench"] == (split == "bench")
        assert md.split_ids(md.load_exercises()) == (sorted(tr_ex), sorted(he_ex), sorted(be_ex))   # fixed seed

    def test_exercise_folders(self):
        ids = [os.path.basename(d) for d in mk.list_exercises(md.EXTRA_DIR)]
        assert len(ids) == 75 and all(re.match(r"s[123]_ex\d\d_", i) for i in ids)
        assert not set(ids) & {os.path.basename(d) for d in mk.list_exercises(md.BENCH_DIR)}
        for d in mk.list_exercises(md.EXTRA_DIR):
            meta, csv = mk.load(d)
            assert meta["id"] == os.path.basename(d) and meta["noise"]["seed"] != 20261009 * 100 + meta["index"]
            assert "half.life" in meta["ground_truth"]["nca"]["linear"]["parameters"]

    @unittest.skipUnless(os.path.exists(apothicaire.MCP_BIN), "caladrius-mcp is not built")
    def test_exercises_regenerate_byte_identical(self):
        import make_exercises as dmk
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "ex")
            dmk.generate(out)
            cmp = filecmp.dircmp(out, md.EXTRA_DIR)
            assert not cmp.left_only and not cmp.right_only
            for d in cmp.common_dirs:
                assert filecmp.cmp(os.path.join(out, d, "data.csv"), os.path.join(md.EXTRA_DIR, d, "data.csv"), shallow=False), d
                assert filecmp.cmp(os.path.join(out, d, "meta.json"), os.path.join(md.EXTRA_DIR, d, "meta.json"), shallow=False), d

    # ---------------------------------------------------------------- class balance printed in the README
    def test_readme_counts_match_the_data(self):
        st = md.stats(*data())
        with open(md.README, encoding="utf-8") as f: text = f.read()
        block = text[text.index(md.COUNTS_BEGIN):text.index(md.COUNTS_END) + len(md.COUNTS_END)]
        assert block == md.counts_block(st), "README counts are stale: run python decision/make_dataset.py"
        for q in ("analysis", "route", "auc_method", *(f"asked_{k}" for k in md.PARAMETERS), "dose_has_unit", "is_not_available", "compare_pair"):
            assert f"`{q}`" in block
        assert sum(st[n]["rows"] for n in md.FILES) >= 3000
        # every declared option of the closed set has examples in train, except the placeholder of a pair-less state and the two
        # options the generator has no request for (2026-10-10, after the review): `not_supported` (out-of-scope asks) and the reversed
        # pair 3+2 (the generator's compare turn always takes the linear analysis as the reference)
        no_rows = {"analysis": {"not_supported"}, "compare_pair": {"3+2"}}
        for q, hist in st["train"]["hist"].items():
            declared = set(md.questions_for([2, 3])[q]["criteria"]) - no_rows.get(q, set())
            assert set(hist) == declared, (q, declared ^ set(hist))


if __name__ == "__main__":
    unittest.main()
