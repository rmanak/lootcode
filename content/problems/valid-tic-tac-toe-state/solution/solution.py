def validTicTacToe(board):
    b = "".join(board)
    xc, oc = b.count("X"), b.count("O")
    if oc != xc and oc != xc - 1:
        return False
    lines = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
             (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]

    def wins(p):
        return any(all(b[i] == p for i in line) for line in lines)

    if wins("X") and xc != oc + 1:
        return False
    if wins("O") and oc != xc:
        return False
    return True
