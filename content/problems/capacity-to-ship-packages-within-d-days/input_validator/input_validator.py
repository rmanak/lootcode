"""Input-constraint validator for problem 'capacity-to-ship-packages-within-d-days'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(weights, days):
    if not isinstance(weights, list):
        return False
    if isinstance(days, bool) or not isinstance(days, int):
        return False
    if len(weights) < 1 or len(weights) > 50000:
        return False
    if days < 1 or days > len(weights):
        return False
    for x in weights:
        if isinstance(x, bool) or not isinstance(x, int) or x < 1 or x > 500:
            return False
    return True
