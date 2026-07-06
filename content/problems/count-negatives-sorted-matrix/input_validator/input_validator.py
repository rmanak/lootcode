"""Input-constraint validator for problem 'count-negatives-sorted-matrix'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(grid):
    if not isinstance(grid, list):
        return False
    if len(grid) < 1 or len(grid) > 1000:
        return False
        
    num_cols = len(grid[0])
    if num_cols < 1 or num_cols > 1000:
        return False
        
    for row in grid:
        if not isinstance(row, list):
            return False
        if len(row) != num_cols:
            return False
        for x in row:
            if isinstance(x, bool) or not isinstance(x, int):
                return False
            if x < -1000000000 or x > 1000000000:
                return False
    return True
