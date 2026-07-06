"""Input-constraint validator for problem 'card-flipping-game'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(fronts, backs):
    if not isinstance(fronts, list) or not isinstance(backs, list):
        return False
    if len(fronts) != len(backs):
        return False
    if len(fronts) < 1 or len(fronts) > 1000:
        return False
    for x in fronts:
        if isinstance(x, bool) or not isinstance(x, int) or x < 1 or x > 2000:
            return False
    for x in backs:
        if isinstance(x, bool) or not isinstance(x, int) or x < 1 or x > 2000:
            return False
    return True
