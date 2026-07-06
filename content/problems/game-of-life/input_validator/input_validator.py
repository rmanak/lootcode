"""Input-constraint validator for problem 'game-of-life'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(board):
    if not isinstance(board, list):
        return False
    m = len(board)
    if m < 1 or m > 25:
        return False
    n = None
    for row in board:
        if not isinstance(row, list):
            return False
        if n is None:
            n = len(row)
        if len(row) != n:
            return False
        if n < 1 or n > 25:
            return False
        for cell in row:
            if isinstance(cell, bool) or not isinstance(cell, int):
                return False
            if cell < 0 or cell > 1:
                return False
    return True
