"""Input-constraint validator for problem 'check-if-array-pairs-are-divisible-by-k'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(arr, k):
    if not isinstance(arr, list):
        return False
    if isinstance(k, bool) or not isinstance(k, int):
        return False
    if len(arr) < 1 or len(arr) > 100000:
        return False
    if len(arr) % 2 != 0:
        return False
    if k < 1 or k > 100000:
        return False
    for x in arr:
        if isinstance(x, bool) or not isinstance(x, int) or x < -1000000000 or x > 1000000000:
            return False
    return True
