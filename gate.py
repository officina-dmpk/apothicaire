"""
Deterministic number gate for Apothicaire (pure Python, no dependency, no model).

Rule: every number the assistant writes must already be in a tool result or in a user message of the
chat, up to the rounding the assistant shows. A number is checked, never judged: set membership.

  check(answer, tool_results, user_texts) -> {
      "numbers_total": checked numbers, "numbers_unverified": those not allowed,
      "numbers_exempt": numbers not checked (see EXEMPTIONS), "findings": [...], "exempt": [...]}

Definitions
  * Extraction: decimal point or comma, thousands separators (space, no-break/narrow space, comma,
    point), scientific notation (2.72e-3, 2,72 x 10^-3, 2,72 x 10⁻³), percentages, a unit written
    after the number (closed table of units). The sign is ignored (46 matches -46).
  * Allowed set: every number of every tool result (JSON numbers exactly as written, numbers inside
    string values, CSV text) and of every user message (the CSV the user pasted included).
    The assistant's own earlier answers are NOT a source. Memory tools (zoom, read_message) are not a
    source either: their results restate old messages and summaries, which could launder a number.
  * Match: an answer number with n significant digits (n = the digits written, at least 2; trailing
    zeros of an integer do not count: 4600 is 2) is allowed if some allowed number, ROUNDED to n
    significant digits, equals it. So 6,98 matches 6.98412 and 7,0 matches 6.98412, 6,99 does not.
    A token that can be read in two ways (1,234 = 1.234 or 1234) passes if either reading matches.
    A token glued from separate numbers (a CSV row 12,205.3 or 10 250) that matches nothing as a whole
    is then checked as its parts.
  * Unit conversions are NOT allowed: 0.00271828 mg/(h.ng/mL) rewritten as 27.1828 is a new number
    that is in no tool result. Differences, ratios, sums and percentages computed by the assistant are
    new numbers too, and are reported. A finding carries the nearest allowed value and, when the number
    is an allowed one times a power of ten, a hint.

EXEMPTIONS (counted in numbers_exempt, never in numbers_total, listed in "exempt"):
  * small_integer: an integer literal 0..20 with no unit, no % and no decimal part (counts, "8 points",
    "AUC(0-inf)"). With a unit it is checked: "5 mg" or "3 h" must be in a source.
  * year: an integer 1900..2100 with no unit.
  * date: the numbers of an ISO date (2026-10-09).
  * label_number: an integer 0..99 right after a label word (step, etape, tour, turn, exercice,
    question, point, sujet, subject, figure, tableau, ...) or a list marker at the start of a line
    ("3." or "2)"); "#17" message references of the memory (any integer).
  * unit_fragment: the 1 of a unit such as 1/h (and any exponent inside a unit, h^2).
  * power_of_ten: a bare 10^k / 10**k / 10⁻³ (a conversion factor named without a mantissa; the
    converted values around it are what gets reported).
  Everything else is checked, including 0,0 and 1,0.
"""
import math, re
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN, InvalidOperation

SPACES = "     "                  # space, no-break, narrow no-break, thin, figure space
_SPC = "    "                     # the unambiguous ones
_MINUS = "-−"
SMALL_INT_MAX = 20
LABEL_INT_MAX = 99

# ---------------------------------------------------------------- tokenising
_NUM_RE = re.compile(r"""
(?<![\w.,])
(?P<num>
    \d{1,3}(?:[     ]\d{3})+(?:[.,]\d+)?
  | \d{1,3}(?:[.,]\d{3})+(?:[.,]\d+)?
  | \d+(?:[.,]\d+)?
)
(?P<exp>
    [eE][-+−]?\d+
  | \s?[x×*·]\s?10\s?(?:\^|\*\*)\s?\(?[-+−]?\d+\)?
  | \s?[x×*·]\s?10[⁺⁻]?[⁰¹²³⁴-⁹]+
)?
(?!\d)(?![.,]\d)
""", re.X)

_POW10_RE = re.compile(r"(?<![\w.,])(?<![x×*·])(?<![x×*·]\s)"
                       r"(?:10\s?(?:\^|\*\*)\s?\(?[-+−]?\d+\)?|10[⁺⁻]?[⁰¹²³⁴-⁹]+)")
_DATE_RE = re.compile(r"(?<!\d)\d{4}-\d{2}-\d{2}(?!\d)")
_LABEL_RE = re.compile(r"(?:\b(?:[ée]tape|etape|step|tour|turn|exercice|exercise|exo|question|partie|part|section|"
                       r"chapitre|chapter|figure|fig|tableau|table|ligne|line|message|msg|point|sujet|subject|"
                       r"patient|animal|rang|rank|n[°o]|no)\.?\s*|#)$", re.I)
_LISTMARK_RE = re.compile(r"^[ \t]*(?:[-*•>][ \t]*)?$")
_SUP = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5",
        "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9"}

# Units that can follow a number. Closed table: an unknown word after a number is not a unit.
_ATOM_RE = re.compile(r"(?:%|‰|°C|(?:[kmMµμnpu]?(?:mol|Hz|g|L|l|M))(?![A-Za-z])|"
                      r"mL|ml|dL|dl|IU|min|h|s|d|j|U)(?![A-Za-zµμ'’])")
_UNIT_EXP_RE = re.compile(r"\^?[-−]?\d+|[⁻−]?[⁰¹²³⁴-⁹]+")

def _read_unit(text, pos):
    """Unit written right after a number (optionally one space away): 'ng/mL', 'h*ng/mL', 'mg/(h.ng/mL)',
    '1/h' (the number is the 1), '%'. Returns (unit string, end offset); ('', pos) if there is none."""
    p = pos
    if p < len(text) and text[p] in SPACES: p += 1
    start, depth, expect_atom = p, 0, True
    last_end = p
    if p < len(text) and text[p] == "/":                # '1/h': the unit starts with a separator
        p += 1
    while p < len(text):
        if text[p] == "(" and expect_atom:
            depth += 1; p += 1; continue
        m = _ATOM_RE.match(text, p)
        if not m: break
        p = m.end()
        em = _UNIT_EXP_RE.match(text, p)
        if em and (text[p] in "^⁻−" or text[p] in _SUP) and m.group(0) not in ("%", "‰"):
            p = em.end()
        while depth and p < len(text) and text[p] == ")":
            depth -= 1; p += 1
        last_end = p; expect_atom = False
        if p < len(text) and text[p] in "/·*.":
            nxt = p + 1
            if nxt < len(text) and (_ATOM_RE.match(text, nxt) or text[nxt] == "("):
                p = nxt; expect_atom = True; continue
        break
    unit = text[start:last_end]
    return (unit, last_end) if unit else ("", pos)

def _sig(digits, has_decimal):
    d = digits.lstrip("0")
    n = len(d) if has_decimal else len(d.rstrip("0"))
    return max(n, 2)

def _dec(s):
    try: return Decimal(s)
    except InvalidOperation: return None

def _readings(num):
    """All readings of a number token as (Decimal, significant digits, is_integer_literal)."""
    if any(c in SPACES for c in num):                                  # 5 038,26
        t = re.sub("[" + re.escape(SPACES) + "]", "", num).replace(",", ".")
        return [(Decimal(t), _sig(t.replace(".", ""), "." in t), "." not in t)]
    seps = [(m.start(), m.group()) for m in re.finditer(r"[.,]", num)]
    if not seps:
        return [(Decimal(num), _sig(num, False), True)]
    kinds = {c for _, c in seps}
    if len(kinds) == 2:                                                # 1,234.5 or 1.234,5
        dec = seps[-1][1]; thou = "," if dec == "." else "."
        t = num.replace(thou, "").replace(dec, ".")
        return [(Decimal(t), _sig(t.replace(".", ""), True), False)]
    if len(seps) >= 2:                                                 # 1,234,567 or 1.234.567
        t = re.sub(r"[.,]", "", num)
        return [(Decimal(t), _sig(t, False), True)]
    i, c = seps[0]; before, after = num[:i], num[i + 1:]
    out = [(Decimal(before + "." + after), _sig(before + after, True), False)]
    if len(after) == 3 and 1 <= len(before) <= 3 and before[0] != "0":    # 1,234: 1.234 or 1234
        out.append((Decimal(before + after), _sig(before + after, False), True))
    return out

def _apply_exp(readings, exp_text):
    if not exp_text: return readings
    e = exp_text.strip()
    m = re.match(r"[eE]([-+−]?\d+)", e)
    if m: k = int(m.group(1).replace("−", "-"))
    else:
        digits = re.search(r"10\s?(?:\^|\*\*)?\s?\(?([-+−]?\d+)\)?$", e)
        if digits and not any(ch in e for ch in _SUP): k = int(digits.group(1).replace("−", "-"))
        else:
            sup = "".join(_SUP.get(ch, "") for ch in e)
            k = int(sup) * (-1 if re.search(r"10[⁻−]", e) else 1)
    return [(v.scaleb(k), s, False) for v, s, _ in readings]

class Num:
    """A number found in a text."""
    __slots__ = ("raw", "start", "end", "unit", "readings", "exempt", "parts", "span_end")
    def __init__(self, raw, start, end, unit, readings, exempt=None, parts=None, span_end=None):
        self.raw, self.start, self.end, self.unit = raw, start, end, unit
        self.readings, self.exempt, self.parts = readings, exempt, parts or []
        self.span_end = end if span_end is None else span_end
    @property
    def text(self):
        return (self.raw + (" " + self.unit if self.unit else "")).strip()
    def __repr__(self): return f"Num({self.text!r}@{self.start}, {[str(v) for v, _, _ in self.readings]})"

def _parts_of(raw, start, unit):
    """A token that is probably several numbers glued by commas or spaces (a CSV row 12,205.3; 10 250)
    read as separate numbers: [Num] or []. Only a token with an ASCII space or with both a comma and a
    point, and no unit after it, is split: a decimal (27,1828) or a single-comma token (472,711) is
    one number."""
    if unit: return []
    if not (" " in raw or ("," in raw and "." in raw)): return []
    pieces = [p for p in re.split(r"[,; ]+", raw) if p]
    if len(pieces) < 2: return []
    out = []
    for p in pieces:
        if not re.fullmatch(r"(?:0|[1-9]\d*)(?:\.\d+)?", p): return []
        out.append(Num(p, start, start + len(raw), "", _readings(p)))
    return out

def extract_numbers(text):
    """Numbers of a text, in order, with unit, readings and exemption reason (None = to be checked)."""
    covered = []                                       # spans claimed by pow10 / dates
    out = []
    for m in _POW10_RE.finditer(text):
        out.append(Num(m.group(0), m.start(), m.end(), "", [(Decimal(10), 2, False)], "power_of_ten"))
        covered.append((m.start(), m.end()))
    dates = [(m.start(), m.end()) for m in _DATE_RE.finditer(text)]
    covered += dates
    inside = lambda a, b: any(a < e and b > s for s, e in covered)
    skip_until = 0
    for m in _NUM_RE.finditer(text):
        s, e = m.start(), m.end()
        if inside(s, e) or s < skip_until: continue          # inside a date, a 10^k or the unit of the previous number
        raw = m.group("num")
        readings = _apply_exp(_readings(raw), m.group("exp"))
        unit, uend = _read_unit(text, e)
        skip_until = uend
        n = Num(raw if not m.group("exp") else text[s:e], s, e, unit, readings, span_end=uend)
        if not m.group("exp"): n.parts = _parts_of(raw, s, unit)
        if raw == "1" and not m.group("exp") and unit.startswith("/"): n.exempt = "unit_fragment"   # the 1 of 1/h
        out.append(n)
    for s, e in dates:
        for m in re.finditer(r"\d+", text[s:e]):
            out.append(Num(m.group(0), s + m.start(), s + m.end(), "", [(Decimal(m.group(0)), 2, True)], "date"))
    out.sort(key=lambda n: (n.start, n.end))
    for n in out:
        if n.exempt is None: n.exempt = _exemption(text, n)
    return out

def _exemption(text, n):
    if len(n.readings) != 1 or not n.readings[0][2] or n.unit or "e" in n.raw.lower() or \
            "×" in n.raw or any(c in n.raw for c in SPACES + ",."):
        return None
    v = int(n.readings[0][0])
    if v <= SMALL_INT_MAX: return "small_integer"
    if 1900 <= v <= 2100 and len(n.raw) == 4: return "year"
    before = text[:n.start]
    if before.endswith("#"): return "label_number"
    if v <= LABEL_INT_MAX:
        if _LABEL_RE.search(before[-24:]): return "label_number"
        line_start = before.rfind("\n") + 1
        after = text[n.end:n.end + 2]
        if _LISTMARK_RE.match(before[line_start:]) and after[:1] in (".", ")") and after[1:2] in (" ", "\t", ""):
            return "label_number"
    return None

# ---------------------------------------------------------------- allowed set
class Allowed:
    __slots__ = ("value", "text", "source")
    def __init__(self, value, text, source): self.value, self.text, self.source = value, text, source

def _bag_readings(token, generous):
    """Readings of a run of digits and separators from a source text. Tool results use the engine's
    format (point decimal, no grouping); a user may write anything, so every plausible reading counts."""
    outs = []
    pieces = re.split(r"[,;]", token)
    for p in pieces:
        if re.fullmatch(r"\d+(?:\.\d+)?", p): outs.append(Decimal(p))
    if generous:
        for v, _, _ in _readings_safe(token): outs.append(v)
        if "," in token and "." not in token and token.count(",") == 1:
            outs.append(Decimal(token.replace(",", ".")))
    return outs

def _readings_safe(token):
    try: return _readings(token)
    except Exception: return []

_BAG_RE = re.compile(r"\d+(?:[.,]\d+)*(?:[eE][-+]?\d+)?")

def _numbers_in_string(s, generous, label, acc):
    for m in _BAG_RE.finditer(s):
        tok = m.group(0)
        mant, ex = re.fullmatch(r"(.*?)(?:[eE]([-+]?\d+))?", tok).groups()
        for v in _bag_readings(mant, generous):
            if ex: v = v.scaleb(int(ex))
            acc.append(Allowed(abs(v), tok if re.fullmatch(r"\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", tok) else format(abs(v), "f"), label))
    if generous:
        for n in extract_numbers(s):
            for v, _, _ in n.readings: acc.append(Allowed(abs(v), n.raw, label))
    return acc

def _walk_json(x, label, acc):
    if isinstance(x, bool) or x is None: return
    if isinstance(x, Decimal): acc.append(Allowed(abs(x), str(x), label))
    elif isinstance(x, str): _numbers_in_string(x, False, label, acc)
    elif isinstance(x, dict):
        for v in x.values(): _walk_json(v, label, acc)
    elif isinstance(x, list):
        for v in x: _walk_json(v, label, acc)

def allowed_numbers(tool_results=(), user_texts=()):
    """The allowed set: numbers of the tool results (JSON numbers exactly as written, numbers inside
    strings) and of the user messages. See the module docstring for what is not a source."""
    import json
    acc = []
    for i, t in enumerate(tool_results):
        label = f"tool result {i + 1}"
        try: _walk_json(json.loads(t, parse_float=Decimal, parse_int=Decimal), label, acc)
        except (ValueError, TypeError): _numbers_in_string(str(t), False, label, acc)
    for i, t in enumerate(user_texts):
        _numbers_in_string(str(t), True, f"user message {i + 1}", acc)
    seen, out = set(), []
    for a in acc:                                       # one entry per distinct value
        if a.value in seen: continue
        seen.add(a.value); out.append(a)
    return out

# ---------------------------------------------------------------- matching
def round_sig(x, n, mode=ROUND_HALF_UP):
    """x rounded to n significant digits (exact Decimal arithmetic)."""
    if x == 0: return Decimal(0)
    return x.quantize(Decimal(1).scaleb(x.adjusted() - n + 1), rounding=mode)

def _matches(c, n, allowed_values, cache):
    key = n
    if key not in cache:
        cache[key] = {round_sig(a, n, m) for a in allowed_values for m in (ROUND_HALF_UP, ROUND_HALF_EVEN)}
    return abs(c) in cache[key]

def _nearest(c, allowed):
    best, bd = None, None
    for a in allowed:
        if a.value == 0 or c == 0: continue
        d = abs(math.log10(float(c) / float(a.value))) if a.value > 0 and c > 0 else None
        if d is not None and (bd is None or d < bd): best, bd = a, d
    return best

def _hint(c, n, allowed):
    if n < 3: return None                                # with 2 digits a power-of-ten match is often a coincidence
    for a in allowed:
        if a.value == 0 or c == 0: continue
        k = round(math.log10(float(c) / float(a.value)))
        if k != 0 and abs(k) <= 12 and round_sig(a.value.scaleb(k), n) == round_sig(c, n):
            return f"{a.text} x 10^{k}: a unit conversion or a rescaling of a tool value"
    return None

def _line_of(text, pos): return text.count("\n", 0, pos) + 1

def check(answer, tool_results=(), user_texts=(), allowed=None):
    """Checks the numbers of `answer`. `allowed` (from allowed_numbers) can be passed to avoid recomputing."""
    allowed = allowed_numbers(tool_results, user_texts) if allowed is None else allowed
    values = [a.value for a in allowed]
    cache = {}
    total = unverified = 0
    findings, exempt = [], []

    def ok(n):
        return any(_matches(abs(v), s, values, cache) for v, s, _ in n.readings)

    def report(n):
        v, s, _ = n.readings[0]
        near = _nearest(abs(v), allowed)
        return {"number": n.raw, "text": n.text, "value": str(v.normalize() if v != 0 else 0),
                "position": [n.start, n.end], "line": _line_of(answer, n.start), "unit": n.unit,
                "significant_digits": s,
                "nearest_allowed": near.text if near else None,
                "nearest_source": near.source if near else None,
                "hint": _hint(abs(v), s, allowed)}

    for n in extract_numbers(answer):
        if n.exempt:
            exempt.append({"number": n.raw, "position": [n.start, n.end], "reason": n.exempt}); continue
        if ok(n):
            total += 1; continue
        if n.parts:                                      # glued token: check the pieces instead
            for p in n.parts:
                total += 1
                if not ok(p): unverified += 1; findings.append(report(p))
            continue
        total += 1; unverified += 1; findings.append(report(n))
    return {"numbers_total": total, "numbers_unverified": unverified, "numbers_exempt": len(exempt),
            "findings": findings, "exempt": exempt}

# ---------------------------------------------------------------- messages built from the findings
def badge(findings, limit=8):
    """The visible mark added to an answer that still has unverified numbers."""
    if not findings: return ""
    shown = []
    for f in findings:
        if f["text"] not in shown: shown.append(f["text"])
    more = f", +{len(shown) - limit}" if len(shown) > limit else ""
    return f"⚠ {len(findings)} number(s) not found in tool results: {', '.join(shown[:limit])}{more}"

def reminder(findings, limit=12):
    """System reminder appended at the END of the messages for the one regeneration (the static
    prompt prefix is not touched)."""
    shown = []
    for f in findings:
        if f["text"] not in shown: shown.append(f["text"])
    lines = [f"- {t}" for t in shown[:limit]]
    return ("[system reminder] Your last answer contains numbers that appear in no tool result and in no "
            "user message:\n" + "\n".join(lines) + "\n"
            "Write the answer again. Rule: quote tool values verbatim, never convert (no unit conversion, no "
            "multiplication by the dose or by 10^3), never compute new values (no sums, differences, ratios, "
            "percentages). Give each value with the unit the tool gave. If a number you want is not in the "
            "tool results, say that Caladrius did not return it.")
