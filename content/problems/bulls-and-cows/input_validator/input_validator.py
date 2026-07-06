"""Input-constraint validator for problem 'bulls-and-cows'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(secret, guess):
    if not isinstance(secret, str) or not isinstance(guess, str):
        return False
    if len(secret) != len(guess):
        return False
    if len(secret) < 1:
        return False
    for c in secret:
        if not ('0' <= c <= '9'):
            return False
    for c in guess:
        if not ('0' <= c <= '9'):
            return False
    return True
