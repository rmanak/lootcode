"""Input-constraint validator for problem 'count-unique-characters-of-all-substrings-of-a-given-string'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(s):
    if not isinstance(s, str):
        return False
    if len(s) < 0 or len(s) > 10000:
        return False
    for c in s:
        if not ('A' <= c <= 'Z'):
            return False
    return True
