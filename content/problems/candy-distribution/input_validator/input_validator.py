"""Input-constraint validator for problem 'candy-distribution'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(ratings):
    if not isinstance(ratings, list):
        return False
    if len(ratings) < 1 or len(ratings) > 20000:
        return False
    for x in ratings:
        if isinstance(x, bool) or not isinstance(x, int) or x < 0 or x > 1000000000:
            return False
    return True
