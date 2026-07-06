"""Input-constraint validator for problem 'count-servers-that-communicate'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(grid):
    if not isinstance(grid, list):
        return False
    m = len(grid)
    if m < 1 or m > 250:
        return False
    for row in grid:
        if not isinstance(row, list):
            return False
        n = len(row)
        if n < 1 or n > 250:
            return False
        for x in row:
            if isinstance(x, bool) or not isinstance(x, int) or x < 0 or x > 1:
                return False
    return True
