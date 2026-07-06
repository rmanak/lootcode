"""Input-constraint validator for problem 'browser-history'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(homepage, operations):
    if not isinstance(homepage, str):
        return False
    if len(homepage) < 1:
        return False
    if not isinstance(operations, list):
        return False
    if len(operations) < 1 or len(operations) > 5000:
        return False
    for op in operations:
        if not isinstance(op, list):
            return False
        if len(op) != 2:
            return False
        action = op[0]
        value = op[1]
        if not isinstance(action, str):
            return False
        if action == "visit":
            if not isinstance(value, str) or len(value) < 1:
                return False
        elif action == "back":
            if isinstance(value, bool) or not isinstance(value, int):
                return False
            if value < 1:
                return False
        elif action == "forward":
            if isinstance(value, bool) or not isinstance(value, int):
                return False
            if value < 1:
                return False
        else:
            return False
    return True
