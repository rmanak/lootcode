"""Input-constraint validator for problem 'avoid-flood-in-the-city'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(rains):
    if not isinstance(rains, list):
        return False
    if len(rains) < 1 or len(rains) > 100000:
        return False
    for x in rains:
        if isinstance(x, bool) or not isinstance(x, int) or x < 0 or x > 1000000000:
            return False
    return True
