"""Input-constraint validator for problem 'friends-of-appropriate-ages'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(ages):
    if not isinstance(ages, list):
        return False
    if len(ages) < 1 or len(ages) > 20000:
        return False
    for x in ages:
        if isinstance(x, bool) or not isinstance(x, int) or x < 1 or x > 120:
            return False
    return True
