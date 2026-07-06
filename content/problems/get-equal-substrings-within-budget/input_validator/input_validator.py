"""Input-constraint validator for problem 'get-equal-substrings-within-budget'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(s, t, maxCost):
    if not isinstance(s, str):
        return False
    if not isinstance(t, str):
        return False
    if isinstance(maxCost, bool) or not isinstance(maxCost, int):
        return False
    if len(s) != len(t):
        return False
    if len(s) < 1 or len(s) > 100000:
        return False
    if maxCost < 0 or maxCost > 1000000:
        return False
    for c in s:
        if not ('a' <= c <= 'z'):
            return False
    for c in t:
        if not ('a' <= c <= 'z'):
            return False
    return True
