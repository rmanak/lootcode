"""Input-constraint validator for problem 'count-triplets-that-can-form-two-arrays-of-equal-xor'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(arr):
    if not isinstance(arr, list):
        return False
    if len(arr) < 1 or len(arr) > 300:
        return False
    for x in arr:
        if isinstance(x, bool) or not isinstance(x, int) or x < 1 or x > 100000000:
            return False
    return True
