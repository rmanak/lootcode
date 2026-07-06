"""Input-constraint validator for problem 'calendar-double-booking'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(operations):
    if not isinstance(operations, list):
        return False
    if len(operations) < 1 or len(operations) > 1000:
        return False
    for op in operations:
        if not isinstance(op, list):
            return False
        if len(op) != 3:
            return False
        if op[0] != "book":
            return False
        start = op[1]
        end = op[2]
        if isinstance(start, bool) or not isinstance(start, int):
            return False
        if isinstance(end, bool) or not isinstance(end, int):
            return False
        if start < 0 or start >= end:
            return False
        if end > 1000000000:
            return False
    return True
