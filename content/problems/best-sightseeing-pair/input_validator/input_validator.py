"""Input-constraint validator for problem 'best-sightseeing-pair'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(values):
    if not isinstance(values, list):
        return False
    if len(values) < 2 or len(values) > 50000:
        return False
    for x in values:
        if isinstance(x, bool) or not isinstance(x, int) or x < 1 or x > 1000:
            return False
    return True
