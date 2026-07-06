"""Input-constraint validator for problem 'container-with-most-water'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(height):
    if not isinstance(height, list):
        return False
    if len(height) < 2 or len(height) > 100000:
        return False
    for x in height:
        if isinstance(x, bool) or not isinstance(x, int) or x < 0 or x > 10000:
            return False
    return True
