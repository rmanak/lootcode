"""Input-constraint validator for problem 'find-the-minimum-number-of-fibonacci-numbers-whose-sum-is-k'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(k):
    if isinstance(k, bool) or not isinstance(k, int):
        return False
    if k < 1 or k > 1000000000:
        return False
    return True
