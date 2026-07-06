"""Input-constraint validator for problem 'autocomplete-top-k'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(k, operations):
    if isinstance(k, bool) or not isinstance(k, int):
        return False
    if k < 1 or k > 10:
        return False

    if not isinstance(operations, list):
        return False
    if len(operations) < 1 or len(operations) > 10000:
        return False

    for op in operations:
        if not isinstance(op, list):
            return False

        if len(op) == 3 and op[0] == "add":
            sentence = op[1]
            count = op[2]
            if not isinstance(sentence, str) or len(sentence) < 1:
                return False
            for c in sentence:
                if not (c.islower() or c == ' '):
                    return False
            if isinstance(count, bool) or not isinstance(count, int):
                return False
            if count < 1 or count > 1000000:
                return False
        elif len(op) == 2 and op[0] == "query":
            prefix = op[1]
            if not isinstance(prefix, str):
                return False
        else:
            return False

    return True
