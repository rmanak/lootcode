"""Input-constraint validator for problem 'battleships-in-a-board'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(board):
    if board is None or not isinstance(board, list):
        return False
    for row in board:
        if not isinstance(row, str):
            return False
    if len(board) == 0:
        return True
    row_len = len(board[0])
    for row in board:
        if len(row) != row_len:
            return False
    for row in board:
        for ch in row:
            if ch != 'X' and ch != '.':
                return False
    rows = len(board)
    cols = row_len
    for i in range(rows):
        for j in range(cols):
            if board[i][j] == 'X':
                has_right = j + 1 < cols and board[i][j + 1] == 'X'
                has_bottom = i + 1 < rows and board[i + 1][j] == 'X'
                if has_right and has_bottom:
                    return False
    return True
