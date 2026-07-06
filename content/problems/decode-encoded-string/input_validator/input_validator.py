"""Input-constraint validator for problem 'decode-encoded-string'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(s):
    if not isinstance(s, str):
        return False
    if len(s) < 1 or len(s) > 30000:
        return False
    for c in s:
        if not (('a' <= c <= 'z') or ('0' <= c <= '9') or c in '[]'):
            return False
    return True
