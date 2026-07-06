"""Input-constraint validator for problem 'boolean-parenthesization'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(expr):
    if not isinstance(expr, str):
        return False
    if len(expr) < 1 or len(expr) > 199:
        return False
    if len(expr) % 2 != 1:
        return False
    for i, c in enumerate(expr):
        if i % 2 == 0:
            if c != 'T' and c != 'F':
                return False
        else:
            if c != '&' and c != '|' and c != '^':
                return False
    return True
