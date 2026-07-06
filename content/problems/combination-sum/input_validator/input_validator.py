"""Input-constraint validator for problem 'combination-sum'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(candidates, target):
    if not isinstance(candidates, list):
        return False
    if isinstance(target, bool) or not isinstance(target, int):
        return False
    if len(candidates) < 1 or len(candidates) > 30:
        return False
    if target < 1 or target > 40:
        return False
    for x in candidates:
        if isinstance(x, bool) or not isinstance(x, int) or x < 2 or x > 40:
            return False
    return True
