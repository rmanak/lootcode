def solveNQueens(n):
    res = []
    cols, diag, anti, placement = set(), set(), set(), []

    def bt(row):
        if row == n:
            res.append(["".join("Q" if placement[r] == c else "." for c in range(n))
                        for r in range(n)])
            return
        for c in range(n):
            if c in cols or (row - c) in diag or (row + c) in anti:
                continue
            cols.add(c); diag.add(row - c); anti.add(row + c); placement.append(c)
            bt(row + 1)
            cols.discard(c); diag.discard(row - c); anti.discard(row + c); placement.pop()

    bt(0)
    return res
