"""Input-constraint validator for problem 'cherry-pickup-two-robots'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(grid):
    if not isinstance(grid, list):
        return False
    rows = len(grid)
    if rows < 1 or rows > 70:
        return False
    cols = len(grid[0])
    if cols < 1 or cols > 70:
        return False
    for r in grid:
        if not isinstance(r, list):
            return False
        if len(r) != cols:
            return False
        for x in r:
            if isinstance(x, bool) or not isinstance(x, int):
                return False
            if x < 0 or x > 100:
                return False
    return True
