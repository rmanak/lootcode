"""Input-constraint validator for problem 'consistent-hash-ring'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(operations):
    if not isinstance(operations, list):
        return False
    if len(operations) < 1 or len(operations) > 100000:
        return False
    for op in operations:
        if not isinstance(op, list):
            return False
        if len(op) != 2:
            return False
        if not isinstance(op[0], str):
            return False
        if op[0] not in ("addServer", "removeServer", "getServer"):
            return False
        if isinstance(op[1], bool) or not isinstance(op[1], int):
            return False
        if op[1] < 0 or op[1] > 1000000000:
            return False
    return True
