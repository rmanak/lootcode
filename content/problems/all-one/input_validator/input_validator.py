"""Input-constraint validator for problem 'all-one'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(operations):
    if not isinstance(operations, list):
        return False
    if len(operations) < 1 or len(operations) > 50000:
        return False

    counts = {}

    for op in operations:
        if not isinstance(op, list):
            return False

        if len(op) == 2:
            if not isinstance(op[0], str) or not isinstance(op[1], str):
                return False
            if op[0] == "inc":
                counts[op[1]] = counts.get(op[1], 0) + 1
            elif op[0] == "dec":
                if op[1] not in counts or counts[op[1]] <= 0:
                    return False
                counts[op[1]] -= 1
                if counts[op[1]] == 0:
                    del counts[op[1]]
            else:
                return False
        elif len(op) == 1:
            if not isinstance(op[0], str):
                return False
            if op[0] not in ("getMaxKey", "getMinKey"):
                return False
        else:
            return False

    return True
