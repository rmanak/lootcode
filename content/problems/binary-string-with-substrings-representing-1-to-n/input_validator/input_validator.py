"""Input-constraint validator for problem 'binary-string-with-substrings-representing-1-to-n'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(S, N):
    if not isinstance(S, str):
        return False
    if isinstance(N, bool) or not isinstance(N, int):
        return False
    if len(S) < 1 or len(S) > 1000:
        return False
    if N < 1 or N > 1000000000:
        return False
    for c in S:
        if c != '0' and c != '1':
            return False
    return True
