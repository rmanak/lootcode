"""Input-constraint validator for problem 'check-if-a-string-can-break-another-string'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(s1, s2):
    if not isinstance(s1, str) or not isinstance(s2, str):
        return False
    if len(s1) != len(s2):
        return False
    if len(s1) < 1 or len(s1) > 100000:
        return False
    for c in s1:
        if not ('a' <= c <= 'z'):
            return False
    for c in s2:
        if not ('a' <= c <= 'z'):
            return False
    return True
