"""Input-constraint validator for problem 'brace-expansion-ii'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Hand-written: enforces that the expression is a sentence of the
statement's grammar: letters, {e1,e2,...} unions and concatenation, braces balanced.
The generated version skipped this as a "semantic guarantee", which let the
retired test generator bake in a malformed hidden case. Do not regenerate.
"""
_LETTERS = set("abcdefghijklmnopqrstuvwxyz")
_ALLOWED = _LETTERS | set("{},")


def _term(s, i):
    """One or more letters / brace groups; index after it, or None."""
    start = i
    while i < len(s) and (s[i] == "{" or s[i] in _LETTERS):
        if s[i] == "{":
            i = _union(s, i + 1)
            if i is None or i >= len(s) or s[i] != "}":
                return None
        i += 1
    return i if i > start else None


def _union(s, i):
    """term (',' term)* inside a brace group."""
    i = _term(s, i)
    while i is not None and i < len(s) and s[i] == ",":
        i = _term(s, i + 1)
    return i



def validate_input(expression):
    if not isinstance(expression, str):
        return False
    if not (1 <= len(expression) <= 60):
        return False
    if not set(expression) <= _ALLOWED:
        return False
    return _term(expression, 0) == len(expression)
