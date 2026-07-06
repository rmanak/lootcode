"""Input-constraint validator for problem 'asteroid-collision'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(asteroids):
    if not isinstance(asteroids, list):
        return False
    if len(asteroids) > 10000:
        return False
    for x in asteroids:
        if isinstance(x, bool) or not isinstance(x, int):
            return False
        if x < -1000 or x > 1000 or x == 0:
            return False
    return True
