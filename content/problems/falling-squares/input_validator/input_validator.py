"""Input-constraint validator for problem 'falling-squares'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(positions):
    if not isinstance(positions, list):
        return False
    if len(positions) < 1 or len(positions) > 1000:
        return False
    for p in positions:
        if not isinstance(p, list):
            return False
        if len(p) != 2:
            return False
        left, side = p[0], p[1]
        if isinstance(left, bool) or not isinstance(left, int):
            return False
        if isinstance(side, bool) or not isinstance(side, int):
            return False
        if left < 1 or left > 100000000:
            return False
        if side < 1 or side > 100000000:
            return False
    return True
