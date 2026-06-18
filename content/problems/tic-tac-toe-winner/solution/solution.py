def tictactoe(n, moves):
    rows = [[0] * n for _ in range(2)]
    cols = [[0] * n for _ in range(2)]
    diag = [0, 0]
    anti = [0, 0]
    res = []
    for r, c, p in moves:
        pi = p - 1
        rows[pi][r] += 1
        cols[pi][c] += 1
        if r == c:
            diag[pi] += 1
        if r + c == n - 1:
            anti[pi] += 1
        if (rows[pi][r] == n or cols[pi][c] == n or diag[pi] == n
                or anti[pi] == n):
            res.append(p)
        else:
            res.append(0)
    return res
