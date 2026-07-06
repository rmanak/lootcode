"""Input-constraint validator for problem 'boats-to-save-people'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(people, limit):
    if not isinstance(people, list):
        return False
    if len(people) < 1 or len(people) > 50000:
        return False
    if isinstance(limit, bool) or not isinstance(limit, int):
        return False
    if limit < 1 or limit > 30000:
        return False
    for x in people:
        if isinstance(x, bool) or not isinstance(x, int):
            return False
        if x < 1 or x > limit:
            return False
    return True
