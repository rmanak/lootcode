"""Input-constraint validator for problem 'find-latest-group-of-size-m'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(arr, m):
    if not isinstance(arr, list):
        return False
    if isinstance(m, bool) or not isinstance(m, int):
        return False
    n = len(arr)
    if n < 1 or n > 100000:
        return False
    if m < 1 or m > n:
        return False
    for x in arr:
        if isinstance(x, bool) or not isinstance(x, int) or x < 1 or x > n:
            return False
    if len(set(arr)) != n:
        return False
    return True
