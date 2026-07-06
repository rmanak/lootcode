"""Input-constraint validator for problem 'dice-roll-simulation'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(n, rollMax):
    if isinstance(n, bool) or not isinstance(n, int):
        return False
    if n < 1 or n > 5000:
        return False
    if not isinstance(rollMax, list):
        return False
    if len(rollMax) != 6:
        return False
    for x in rollMax:
        if isinstance(x, bool) or not isinstance(x, int):
            return False
        if x < 1 or x > 15:
            return False
    return True
