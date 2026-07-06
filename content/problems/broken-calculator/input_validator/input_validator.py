"""Input-constraint validator for problem 'broken-calculator'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(startValue, target):
    if isinstance(startValue, bool) or not isinstance(startValue, int):
        return False
    if isinstance(target, bool) or not isinstance(target, int):
        return False
    if startValue < 1 or startValue > 1000000000:
        return False
    if target < 1 or target > 1000000000:
        return False
    return True
