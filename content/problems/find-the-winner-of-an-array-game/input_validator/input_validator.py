"""Input-constraint validator for problem 'find-the-winner-of-an-array-game'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(arr, k):
    if not isinstance(arr, list):
        return False
    if len(arr) < 2 or len(arr) > 100000:
        return False
    if isinstance(k, bool) or not isinstance(k, int):
        return False
    if k < 1 or k > 1000000000:
        return False
    for x in arr:
        if isinstance(x, bool) or not isinstance(x, int):
            return False
    if len(arr) != len(set(arr)):
        return False
    return True
