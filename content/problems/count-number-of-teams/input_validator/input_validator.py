"""Input-constraint validator for problem 'count-number-of-teams'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(rating):
    if not isinstance(rating, list):
        return False
    if len(rating) < 1 or len(rating) > 1000:
        return False
    seen = set()
    for x in rating:
        if isinstance(x, bool) or not isinstance(x, int):
            return False
        if x < 1 or x > 100000:
            return False
        if x in seen:
            return False
        seen.add(x)
    return True
