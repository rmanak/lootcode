"""Input-constraint validator for problem 'parse-lisp-expression'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Hand-written: enforces "the expression is well-formed" (the statement's
grammar, single-space separated, every variable bound by an enclosing let) and
"every value fits in a 32-bit signed integer".
The generated version skipped this as a "semantic guarantee", which let the
retired test generator bake in a malformed hidden case. Do not regenerate.
"""
import re

_INT = re.compile(r"-?\d+")
_VAR = re.compile(r"[a-z][a-z0-9]*")
_RESERVED = {"add", "let", "mult"}
_LO, _HI = -2**31, 2**31 - 1


class _Bad(Exception):
    pass


def _eval(toks, i, env):
    """Evaluate the expression at toks[i]; return (value, next index)."""
    if i >= len(toks):
        raise _Bad
    t = toks[i]
    if t != "(":
        if _INT.fullmatch(t):
            v = int(t)
        elif _VAR.fullmatch(t) and t not in _RESERVED and t in env:
            v = env[t]
        else:
            raise _Bad
        if not _LO <= v <= _HI:
            raise _Bad
        return v, i + 1
    if i + 1 >= len(toks):
        raise _Bad
    head, i = toks[i + 1], i + 2
    if head in ("add", "mult"):
        a, i = _eval(toks, i, env)
        b, i = _eval(toks, i, env)
        v = a + b if head == "add" else a * b
    elif head == "let":
        env = dict(env)
        pairs = 0
        # A variable followed by something other than ")" is a binding.
        while (i + 1 < len(toks) and toks[i + 1] != ")" and toks[i] != "("
               and _VAR.fullmatch(toks[i]) and toks[i] not in _RESERVED):
            name = toks[i]
            env[name], i = _eval(toks, i + 1, env)
            pairs += 1
        if pairs == 0:
            raise _Bad
        v, i = _eval(toks, i, env)
    else:
        raise _Bad
    if i >= len(toks) or toks[i] != ")" or not _LO <= v <= _HI:
        raise _Bad
    return v, i + 1


def validate_input(expression):
    if not isinstance(expression, str):
        return False
    if not (1 <= len(expression) <= 2000):
        return False
    toks = re.findall(r"[()]|[^()\s]+", expression)
    # Canonical spacing: one space between tokens, none inside parentheses.
    rendered = " ".join(toks).replace("( ", "(").replace(" )", ")")
    if rendered != expression:
        return False
    try:
        _, end = _eval(toks, 0, {})
    except (_Bad, RecursionError):
        return False
    return end == len(toks)
