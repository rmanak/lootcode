"""Input-constraint validator for problem '3sum-with-multiplicity'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(A, target):
    if not isinstance(A, list):
        return False
    if isinstance(target, bool) or not isinstance(target, int):
        return False
    if len(A) < 3 or len(A) > 3000:
        return False
    if target < 0 or target > 300:
        return False
    for x in A:
        if isinstance(x, bool) or not isinstance(x, int) or x < 0 or x > 100:
            return False
    return True
