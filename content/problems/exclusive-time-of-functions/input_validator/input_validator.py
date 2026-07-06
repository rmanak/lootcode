"""Input-constraint validator for problem 'exclusive-time-of-functions'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(n, logs):
    if isinstance(n, bool) or not isinstance(n, int):
        return False
    if n < 1 or n > 100:
        return False
    if not isinstance(logs, list):
        return False
    if len(logs) < 1 or len(logs) > 500:
        return False
    for x in logs:
        if not isinstance(x, str):
            return False
    return True
