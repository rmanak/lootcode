"""Input-constraint validator for problem 'hit-counter'.

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
    prev_t = 0
    for op in operations:
        if not isinstance(op, list):
            return False
        if len(op) != 2:
            return False
        if op[0] not in ("hit", "getHits"):
            return False
        t = op[1]
        if isinstance(t, bool) or not isinstance(t, int):
            return False
        if t < 1 or t > 2000000000:
            return False
        if t < prev_t:
            return False
        prev_t = t
    return True
