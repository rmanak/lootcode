"""Input-constraint validator for problem 'bulb-switcher-ii'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(n, m):
    if isinstance(n, bool) or not isinstance(n, int):
        return False
    if isinstance(m, bool) or not isinstance(m, int):
        return False
    if n < 0 or n > 1000:
        return False
    if m < 0 or m > 1000:
        return False
    return True
