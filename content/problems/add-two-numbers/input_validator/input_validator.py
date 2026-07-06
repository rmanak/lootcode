"""Input-constraint validator for problem 'add-two-numbers'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(l1, l2):
    if not isinstance(l1, list) or not isinstance(l2, list):
        return False
    if len(l1) < 1 or len(l1) > 100:
        return False
    if len(l2) < 1 or len(l2) > 100:
        return False
    for x in l1:
        if isinstance(x, bool) or not isinstance(x, int) or x < 0 or x > 9:
            return False
    for x in l2:
        if isinstance(x, bool) or not isinstance(x, int) or x < 0 or x > 9:
            return False
    return True
