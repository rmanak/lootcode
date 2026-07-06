"""Input-constraint validator for problem 'car-fleet'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(target, position, speed):
    if isinstance(target, bool) or not isinstance(target, int):
        return False
    if target < 1 or target > 1000000000:
        return False
    if not isinstance(position, list):
        return False
    if not isinstance(speed, list):
        return False
    if len(position) < 1 or len(position) > 100000:
        return False
    if len(speed) < 1 or len(speed) > 100000:
        return False
    if len(position) != len(speed):
        return False
    for x in position:
        if isinstance(x, bool) or not isinstance(x, int):
            return False
        if x >= target:
            return False
    if len(set(position)) != len(position):
        return False
    for x in speed:
        if isinstance(x, bool) or not isinstance(x, int):
            return False
        if x < 1 or x > 1000000:
            return False
    return True
