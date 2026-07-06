"""Input-constraint validator for problem 'complex-number-multiplication'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(num1, num2):
    if isinstance(num1, bool) or not isinstance(num1, str):
        return False
    if isinstance(num2, bool) or not isinstance(num2, str):
        return False

    for num in [num1, num2]:
        if ' ' in num:
            return False
        parts = num.split('+')
        if len(parts) != 2:
            return False
        a_str, b_str = parts
        if not b_str.endswith('i'):
            return False
        b_str = b_str[:-1]
        if len(a_str) == 0 or len(b_str) == 0:
            return False
        try:
            a = int(a_str)
            b = int(b_str)
        except ValueError:
            return False
        if a < -100 or a > 100:
            return False
        if b < -100 or b > 100:
            return False

    return True
