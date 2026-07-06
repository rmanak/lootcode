"""Input-constraint validator for problem 'clumsy-factorial'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(N):
    if isinstance(N, bool) or not isinstance(N, int):
        return False
    if N < 1 or N > 10000:
        return False
    return True
