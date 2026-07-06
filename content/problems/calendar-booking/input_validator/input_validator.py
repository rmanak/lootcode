"""Input-constraint validator for problem 'calendar-booking'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(operations):
    if not isinstance(operations, list):
        return False
    if len(operations) < 1 or len(operations) > 10000:
        return False
    for op in operations:
        if not isinstance(op, list):
            return False
        if len(op) != 3:
            return False
        if not isinstance(op[0], str) or op[0] != "book":
            return False
        if isinstance(op[1], bool) or not isinstance(op[1], int):
            return False
        if isinstance(op[2], bool) or not isinstance(op[2], int):
            return False
        if op[1] < 0 or op[1] >= op[2]:
            return False
        if op[2] > 1000000000:
            return False
    return True
