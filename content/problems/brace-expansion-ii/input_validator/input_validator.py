"""Input-constraint validator for problem 'brace-expansion-ii'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(expression):
    if not isinstance(expression, str):
        return False
    if len(expression) < 1 or len(expression) > 60:
        return False
    for c in expression:
        if c not in "abcdefghijklmnopqrstuvwxyz{}," :
            return False
    return True
