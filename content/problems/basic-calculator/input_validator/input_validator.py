"""Input-constraint validator for problem 'basic-calculator'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(s):
    if not isinstance(s, str):
        return False
    if len(s) < 1 or len(s) > 300000:
        return False
    allowed = set("0123456789+-() ")
    for c in s:
        if c not in allowed:
            return False
    return True
