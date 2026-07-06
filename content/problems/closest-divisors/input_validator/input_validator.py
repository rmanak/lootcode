"""Input-constraint validator for problem 'closest-divisors'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(num):
    if isinstance(num, bool) or not isinstance(num, int):
        return False
    if num < 1 or num > 1000000000:
        return False
    return True
