"""Input-constraint validator for problem 'check-if-a-string-contains-all-binary-codes-of-size-k'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(s, k):
    if not isinstance(s, str):
        return False
    if isinstance(k, bool) or not isinstance(k, int):
        return False
    if len(s) < 1 or len(s) > 500000:
        return False
    if k < 1 or k > 20:
        return False
    for c in s:
        if c != '0' and c != '1':
            return False
    return True
