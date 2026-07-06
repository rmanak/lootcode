"""Input-constraint validator for problem 'daily-temperatures'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(temperatures):
    if not isinstance(temperatures, list):
        return False
    if len(temperatures) < 1 or len(temperatures) > 100000:
        return False
    for x in temperatures:
        if isinstance(x, bool) or not isinstance(x, int) or x < -50 or x > 150:
            return False
    return True
