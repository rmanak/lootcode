"""Input-constraint validator for problem 'angle-between-hands-of-a-clock'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(hour, minutes):
    if isinstance(hour, bool) or not isinstance(hour, int):
        return False
    if isinstance(minutes, bool) or not isinstance(minutes, int):
        return False
    if hour < 1 or hour > 12:
        return False
    if minutes < 0 or minutes > 59:
        return False
    return True
