"""Input-constraint validator for problem 'grid-path-with-move-and-removal-budget'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy every
input constraint in the statement: 1 <= m, n <= 40, a rectangular 0/1 grid,
grid[0][0] == 0, 0 <= nMoves <= 10^4, 0 <= nRemove <= m * n.
"""


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def validate_input(grid, nMoves, nRemove):
    if not isinstance(grid, list) or not (1 <= len(grid) <= 40):
        return False
    m = len(grid)
    if not isinstance(grid[0], list):
        return False
    n = len(grid[0])
    if not (1 <= n <= 40):
        return False
    for row in grid:
        if not isinstance(row, list) or len(row) != n:
            return False
        for cell in row:
            if not _is_int(cell) or cell not in (0, 1):
                return False
    if grid[0][0] != 0:
        return False
    if not _is_int(nMoves) or not (0 <= nMoves <= 10**4):
        return False
    if not _is_int(nRemove) or not (0 <= nRemove <= m * n):
        return False
    return True
