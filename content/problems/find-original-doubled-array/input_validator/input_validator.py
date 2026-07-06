"""Input-constraint validator for problem 'find-original-doubled-array'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(changed):
    if not isinstance(changed, list):
        return False
    if len(changed) < 1 or len(changed) > 100000:
        return False
    for x in changed:
        if isinstance(x, bool) or not isinstance(x, int) or x < 0 or x > 100000:
            return False
    return True
