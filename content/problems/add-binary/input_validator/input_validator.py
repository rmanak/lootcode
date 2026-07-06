"""Input-constraint validator for problem 'add-binary'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(a, b):
    if not isinstance(a, str) or not isinstance(b, str):
        return False
    if len(a) < 1 or len(a) > 10000:
        return False
    if len(b) < 1 or len(b) > 10000:
        return False
    if not all(c in '01' for c in a):
        return False
    if not all(c in '01' for c in b):
        return False
    if len(a) > 1 and a[0] == '0':
        return False
    if len(b) > 1 and b[0] == '0':
        return False
    return True
