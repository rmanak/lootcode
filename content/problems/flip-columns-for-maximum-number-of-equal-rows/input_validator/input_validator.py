"""Input-constraint validator for problem 'flip-columns-for-maximum-number-of-equal-rows'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(matrix):
    if not isinstance(matrix, list):
        return False
    if len(matrix) < 1 or len(matrix) > 300:
        return False
    if not isinstance(matrix[0], list):
        return False
    cols = len(matrix[0])
    if cols < 1 or cols > 300:
        return False
    for row in matrix:
        if not isinstance(row, list) or len(row) != cols:
            return False
        for x in row:
            if isinstance(x, bool) or not isinstance(x, int) or x != 0 and x != 1:
                return False
    return True
