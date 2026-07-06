"""Input-constraint validator for problem 'fraction-to-recurring-decimal'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(numerator, denominator):
    if isinstance(numerator, bool) or not isinstance(numerator, int):
        return False
    if isinstance(denominator, bool) or not isinstance(denominator, int):
        return False
    if numerator < -2147483648 or numerator > 2147483647:
        return False
    if denominator < -2147483648 or denominator > 2147483647:
        return False
    if denominator == 0:
        return False
    return True
