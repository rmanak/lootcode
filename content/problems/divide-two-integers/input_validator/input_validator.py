"""Input-constraint validator for problem 'divide-two-integers'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(dividend, divisor):
    if isinstance(dividend, bool) or not isinstance(dividend, int):
        return False
    if isinstance(divisor, bool) or not isinstance(divisor, int):
        return False
    if dividend < -2147483648 or dividend > 2147483647:
        return False
    if divisor < -2147483648 or divisor > 2147483647:
        return False
    if divisor == 0:
        return False
    return True
