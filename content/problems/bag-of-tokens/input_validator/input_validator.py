"""Input-constraint validator for problem 'bag-of-tokens'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(tokens, P):
    if not isinstance(tokens, list):
        return False
    if isinstance(P, bool) or not isinstance(P, int):
        return False
    if len(tokens) < 0 or len(tokens) > 1000:
        return False
    if P < 0 or P >= 10000:
        return False
    for x in tokens:
        if isinstance(x, bool) or not isinstance(x, int) or x < 0 or x >= 10000:
            return False
    return True
