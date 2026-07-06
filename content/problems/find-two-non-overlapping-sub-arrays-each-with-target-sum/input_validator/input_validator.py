"""Input-constraint validator for problem 'find-two-non-overlapping-sub-arrays-each-with-target-sum'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(arr, target):
    if not isinstance(arr, list):
        return False
    if isinstance(target, bool) or not isinstance(target, int):
        return False
    if len(arr) < 1 or len(arr) > 100000:
        return False
    if target < 1 or target > 100000000:
        return False
    for x in arr:
        if isinstance(x, bool) or not isinstance(x, int) or x < 1 or x > 1000:
            return False
    return True
