"""Scoring of the benchmark: expected-number matching (the gate's rounding rule) and the failure taxonomy.

Pure Python, no model, no engine. Two things:

1. `score_turn(answer, expect, unverified_after)`: does the answer contain the numbers it must contain
   (`expect["must"]`, each a truth value), none of the numbers it must not (`expect["must_not"]`:
   converted or computed values), the words it must (`expect["words"]`), and, for a question whose answer
   is "not available", no number outside the sources (`expect["no_new_numbers"]`)?
   A truth value T is "found" when some number written in the answer, with n significant digits
   (n >= 2, the gate's counting), equals T rounded to n significant digits (half-up or half-even, like
   the gate). A forbidden value F is "hit" with the same rule but only for numbers written with at least
   3 significant digits (a 2-digit number matching by chance is not evidence of a wrong value).

2. `classify(finding, allowed, kind)`: puts one unverified number of the gate into a class. Rules, in order,
   first match wins; a number written with fewer digits than a rule needs falls through to the next rule. They are
   heuristics on top of the deterministic check (the unverified count never depends on them) and some fire by chance:
   `chance_baseline` measures how often on random numbers, and the report prints it:
     recall_error        the turn is a recall turn (the number should have come from the user's message)
     unit_conversion     the number is an allowed number times a power of ten (3 digits or more), or times 60 or
                         1/60 and a power of ten (4 digits or more): a unit factor (ng to mg, h to min, mL to L...)
     arithmetic          (4 digits or more) the sum, difference, product, ratio or percentage ratio of two
                         allowed numbers (a computation the model did itself)
     unlabelled_misread  a near miss of an allowed number: within 2 % of it, or the same digits with one
                         digit changed (a value copied wrongly, or taken from another parameter)
     other               none of the above (an invented value)
"""
import itertools, math, os, re, sys
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.dirname(HERE)
if AGENT not in sys.path: sys.path.insert(0, AGENT)
import gate  # noqa: E402

D = Decimal

# ---------------------------------------------------------------- matching expected numbers
def written_numbers(text):
    """[(readings, raw)] of every number written in `text` (exempt ones included)."""
    return [(n.readings, n.raw) for n in gate.extract_numbers(text)]

def _eq_rounded(truth, v, n):
    return any(gate.round_sig(abs(truth), n, m) == abs(v) for m in (gate.ROUND_HALF_UP, gate.ROUND_HALF_EVEN))

def matches(truth, readings, min_sig=2, first_only=False):
    """Does a written number (its readings) equal `truth` rounded to the digits written? `first_only`: the
    decimal reading only (121.258 is also 121258 for the gate; a forbidden value must not hit on that second reading)."""
    t = D(repr(truth)) if isinstance(truth, float) else D(truth)
    return any(s >= min_sig and _eq_rounded(t, v, s) for v, s, _ in (readings[:1] if first_only else readings))

def find_value(answer, truth, min_sig=2):
    return any(matches(truth, r, min_sig) for r, _ in written_numbers(answer))

def score_turn(answer, expect, unverified_after=0):
    """Correctness of one answer against its expected-answer rule. Returns a dict:
    found / missing (labels of `must`), forbidden (labels of `must_not` that appear), words_missing,
    new_numbers (for `no_new_numbers`), fraction (found / must), correct."""
    nums = written_numbers(answer)
    found, missing, forbidden, words_missing = [], [], [], []
    for item in expect.get("must", []):
        (found if any(matches(item["value"], r) for r, _ in nums) else missing).append(item["label"])
    for item in expect.get("must_not", []):
        if any(matches(item["value"], r, min_sig=3, first_only=True) for r, _ in nums): forbidden.append(item["label"])
    for w in expect.get("words", []):
        if not re.search(w["pattern"], answer, re.I | re.S): words_missing.append(w["label"])
    new_numbers = unverified_after if expect.get("no_new_numbers") else 0
    n_must = len(expect.get("must", []))
    correct = not missing and not forbidden and not words_missing and not new_numbers
    return {"found": found, "missing": missing, "forbidden": forbidden, "words_missing": words_missing,
            "new_numbers": new_numbers, "n_must": n_must,
            "fraction": (len(found) / n_must) if n_must else 1.0, "correct": correct}

# ---------------------------------------------------------------- taxonomy
CLASSES = ("unit_conversion", "arithmetic", "unlabelled_misread", "recall_error", "other")
_POW10 = [10.0 ** k for k in range(-9, 10) if k != 0]
_FACTORS = _POW10 + [60.0 * p for p in [1.0] + _POW10] + [p / 60.0 for p in [1.0] + _POW10]

def _tol(n):
    """Relative half-width of a rounding to n significant digits (generous by a factor 1.01)."""
    return 0.5 * 10.0 ** (1 - n) * 1.01

def _close(c, r, n):
    """Float prefilter, then the exact rule: c equals r rounded to n significant digits."""
    if r <= 0 or abs(r - c) > _tol(n) * c * 10: return False
    return _eq_rounded(D(repr(r)), D(repr(c)), n)

def _distinct_values(allowed):
    seen, out = set(), []
    for a in allowed:
        if a.value > 0 and a.value not in seen: seen.add(a.value); out.append(a.value)
    return out

def _digits(x):
    return re.sub(r"\D", "", format(x.normalize(), "f")).strip("0")

def _near_miss(c, vals):
    cd = _digits(c)
    for a in vals:
        if c != a and abs(c - a) <= D("0.02") * a: return True
        ad = _digits(a)
        if len(ad) == len(cd) >= 3 and sum(x != y for x, y in zip(ad, cd)) == 1: return True
    return False

def classify(finding, allowed, kind=None):
    """Class of one unverified number. `finding` is a gate finding (value, significant_digits, ...),
    `allowed` the gate's allowed set (gate.allowed_numbers), `kind` the question type of the turn."""
    if kind == "recall": return "recall_error"
    cd = abs(D(finding["value"])); n = max(finding.get("significant_digits", 2), 2)
    if cd == 0: return "other"
    c = float(cd); vals = _distinct_values(allowed); fl = [float(v) for v in vals]
    if n >= 3:                                                       # 1. a unit factor; with 3 digits only a power of ten
        factors = _FACTORS if n >= 4 else _POW10                      # (x 60 and 1/60 match by chance too often)
        for a in fl:
            for f in factors:
                if _close(c, a * f, n): return "unit_conversion"
    if n >= 4:                                                       # 2. arithmetic on two allowed numbers
        pool = fl if len(fl) <= 250 else fl[:250]                     # (with fewer digits it is chance, see chance_baseline)
        for a, b in itertools.permutations(pool, 2):
            for r in (a - b, a + b, a / b, a / b * 100.0, (a - b) / b * 100.0, a * b):
                if _close(c, r, n): return "arithmetic"
    if _near_miss(cd, vals): return "unlabelled_misread"            # 3. a copy that is not verbatim
    return "other"

def classify_all(findings, allowed, kind=None):
    return [classify(f, allowed, kind) for f in findings]

def chance_baseline(allowed, n=100, seed=0, digits=3):
    """How the rules classify RANDOM numbers (log-uniform over the allowed set's range, `digits` significant
    digits): the share of each class that is chance, not evidence. Deterministic for a seed."""
    import random
    rng = random.Random(seed)
    vals = [float(v) for v in _distinct_values(allowed)] or [1.0]
    lo, hi = math.log10(min(vals)) - 1, math.log10(max(vals)) + 1
    out = {c: 0 for c in CLASSES}
    for _ in range(n):
        x = float(f"{10 ** rng.uniform(lo, hi):.{digits}g}")
        f = {"value": repr(x), "significant_digits": digits}
        out[classify(f, allowed)] += 1
    return out
