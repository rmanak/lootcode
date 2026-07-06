"""Input-constraint validator for problem 'dota2-senate'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(senate):
    if not isinstance(senate, str):
        return False
    if len(senate) < 1 or len(senate) > 10000:
        return False
    for c in senate:
        if c != 'R' and c != 'D':
            return False
    return True
