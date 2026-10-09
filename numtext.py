"""Display of a number in a digest: shared by apothicaire.py (the tool results shown to the model) and decision/harness.py
(the French templates). Pure functions, no dependency, no digit is ever changed."""
import re

_TRAILING_ZERO_RE = re.compile(r"(?<![\d.])(-?\d+)\.0(?![\deE])")

def value_text(v):
    """A digest value as shown ("2.108 mg/L", or a bare number such as the adjusted R²), with one display change: the ".0" that
    Python prints after an integral float is dropped (the digest rounds to 6 significant digits, so "1701680.0" would claim 8 of
    them; "1701680" has 6 by the gate's counting). The digits are never changed."""
    return _TRAILING_ZERO_RE.sub(lambda m: m.group(1), v if isinstance(v, str) else f"{v}")
