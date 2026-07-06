"""Input-constraint validator for problem 'detect-cycles-in-2d-grid'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(grid):
    if not isinstance(grid, list):
        return False
    if len(grid) < 1:
        return False
    row_len = None
    for row in grid:
        if not isinstance(row, str):
            return False
        if row_len is None:
            row_len = len(row)
        elif len(row) != row_len:
            return False
        for ch in row:
            if not ('a' <= ch <= 'z'):
                return False
    return True
