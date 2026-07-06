"""Input-constraint validator for problem 'form-largest-integer-with-digits-that-add-up-to-target'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(cost, target):
    if not isinstance(cost, list):
        return False
    if isinstance(target, bool) or not isinstance(target, int):
        return False
    if len(cost) != 9:
        return False
    if target < 1 or target > 5000:
        return False
    for x in cost:
        if isinstance(x, bool) or not isinstance(x, int) or x < 1 or x > 5000:
            return False
    return True
