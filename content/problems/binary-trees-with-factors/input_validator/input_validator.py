"""Input-constraint validator for problem 'binary-trees-with-factors'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(arr):
    if not isinstance(arr, list):
        return False
    if len(arr) < 1 or len(arr) > 1000:
        return False
    for x in arr:
        if isinstance(x, bool) or not isinstance(x, int):
            return False
        if x < 2 or x > 1000000000:
            return False
    if len(set(arr)) != len(arr):
        return False
    return True
