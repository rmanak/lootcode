"""Input-constraint validator for problem 'count-square-submatrices-with-all-ones'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(matrix):
    if not isinstance(matrix, list):
        return False
    m = len(matrix)
    if m < 1 or m > 300:
        return False
    n = len(matrix[0])
    if n < 1 or n > 300:
        return False
    for row in matrix:
        if not isinstance(row, list):
            return False
        if len(row) != n:
            return False
        for x in row:
            if isinstance(x, bool) or not isinstance(x, int) or x < 0 or x > 1:
                return False
    return True
