"""Input-constraint validator for problem 'flip-string-to-monotone-increasing'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(S):
    if not isinstance(S, str):
        return False
    if len(S) < 1 or len(S) > 20000:
        return False
    for c in S:
        if c != '0' and c != '1':
            return False
    return True
