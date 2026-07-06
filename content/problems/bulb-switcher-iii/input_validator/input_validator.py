"""Input-constraint validator for problem 'bulb-switcher-iii'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(light):
    if not isinstance(light, list):
        return False
    n = len(light)
    if n < 1 or n > 50000:
        return False
    seen = set()
    for x in light:
        if isinstance(x, bool) or not isinstance(x, int):
            return False
        if x < 1 or x > n:
            return False
        if x in seen:
            return False
        seen.add(x)
    return True
