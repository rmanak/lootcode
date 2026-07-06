"""Input-constraint validator for problem 'combinations'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(n, k):
    if isinstance(n, bool) or not isinstance(n, int):
        return False
    if isinstance(k, bool) or not isinstance(k, int):
        return False
    if n < 1 or n > 20:
        return False
    if k < 1 or k > n:
        return False
    return True
