"""Input-constraint validator for problem 'basic-calculator-ii'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Hand-written: enforces "s is a valid expression" (number (op number)*,
spaces between tokens) and "division is never by zero" (no zero literal after /).
The generated version skipped this as a "semantic guarantee", which let the
retired test generator bake in a malformed hidden case. Do not regenerate.
"""
import re

_ALLOWED = set("0123456789+-*/ ")


def validate_input(s):
    if not isinstance(s, str):
        return False
    if len(s) < 1 or len(s) > 300000:
        return False
    if not set(s) <= _ALLOWED:
        return False
    # Spaces only separate tokens, so "1 2" yields two adjacent numbers -> invalid.
    tokens = re.findall(r"\d+|[-+*/]", s)
    if len(tokens) % 2 == 0:
        return False
    for i, tok in enumerate(tokens):
        if tok.isdigit() != (i % 2 == 0):
            return False
        # A divisor is always a bare literal (no parentheses); compare digits
        # rather than int() so a 300k-digit number can't trip the str->int limit.
        if tok == "/" and not tokens[i + 1].strip("0"):
            return False
    return True
