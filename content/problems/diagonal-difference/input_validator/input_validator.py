"""Input-constraint validator for problem 'diagonal-difference'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(matrix):
    if not isinstance(matrix, list):
        return False
    n = len(matrix)
    if n < 1 or n > 1000:
        return False
    for row in matrix:
        if not isinstance(row, list):
            return False
        if len(row) != n:
            return False
        for x in row:
            if isinstance(x, bool) or not isinstance(x, int):
                return False
            if x < -10000 or x > 10000:
                return False
    return True
