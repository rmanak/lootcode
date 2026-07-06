"""Input-constraint validator for problem 'array-nesting'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(A):
    if not isinstance(A, list):
        return False
    N = len(A)
    if N < 1 or N > 20000:
        return False
    for x in A:
        if isinstance(x, bool) or not isinstance(x, int):
            return False
    if set(A) != set(range(N)):
        return False
    return True
