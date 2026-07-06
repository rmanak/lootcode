"""Input-constraint validator for problem 'can-convert-string-in-k-moves'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(s, t, k):
    if not isinstance(s, str):
        return False
    if not isinstance(t, str):
        return False
    if isinstance(k, bool) or not isinstance(k, int):
        return False
    if len(s) < 1 or len(s) > 100000:
        return False
    if len(t) < 1 or len(t) > 100000:
        return False
    if k < 0 or k > 1000000000:
        return False
    for c in s:
        if not ('a' <= c <= 'z'):
            return False
    for c in t:
        if not ('a' <= c <= 'z'):
            return False
    return True
