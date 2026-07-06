"""Input-constraint validator for problem 'check-if-word-is-valid-after-substitutions'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(s):
    if not isinstance(s, str):
        return False
    if len(s) < 1 or len(s) > 20000:
        return False
    for ch in s:
        if ch not in ('a', 'b', 'c'):
            return False
    return True
