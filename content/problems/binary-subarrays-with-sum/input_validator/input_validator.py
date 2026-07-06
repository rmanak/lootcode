"""Input-constraint validator for problem 'binary-subarrays-with-sum'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(A, S):
    if not isinstance(A, list):
        return False
    if isinstance(S, bool) or not isinstance(S, int):
        return False
    if len(A) < 1 or len(A) > 30000:
        return False
    if S < 0 or S > len(A):
        return False
    for x in A:
        if isinstance(x, bool) or not isinstance(x, int) or (x != 0 and x != 1):
            return False
    return True
