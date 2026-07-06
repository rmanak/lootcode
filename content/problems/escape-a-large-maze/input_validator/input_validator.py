"""Input-constraint validator for problem 'escape-a-large-maze'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(blocked, source, target):
    if not isinstance(blocked, list):
        return False
    if len(blocked) < 0 or len(blocked) > 200:
        return False
    for cell in blocked:
        if not isinstance(cell, list):
            return False
        if len(cell) != 2:
            return False
        for coord in cell:
            if isinstance(coord, bool) or not isinstance(coord, int):
                return False
            if coord < 0 or coord >= 1000000:
                return False
    if not isinstance(source, list):
        return False
    if len(source) != 2:
        return False
    for coord in source:
        if isinstance(coord, bool) or not isinstance(coord, int):
            return False
        if coord < 0 or coord >= 1000000:
            return False
    if not isinstance(target, list):
        return False
    if len(target) != 2:
        return False
    for coord in target:
        if isinstance(coord, bool) or not isinstance(coord, int):
            return False
        if coord < 0 or coord >= 1000000:
            return False
    if source == target:
        return False
    return True
