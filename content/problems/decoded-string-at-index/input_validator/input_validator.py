"""Input-constraint validator for problem 'decoded-string-at-index'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(S, K):
    if not isinstance(S, str):
        return False
    if isinstance(K, bool) or not isinstance(K, int):
        return False
    if len(S) < 2 or len(S) > 100:
        return False
    if not S[0].isalpha():
        return False
    for c in S:
        if c.isdigit():
            if c < '2' or c > '9':
                return False
    if K < 1 or K >= 9223372036854775808:
        return False
    return True
