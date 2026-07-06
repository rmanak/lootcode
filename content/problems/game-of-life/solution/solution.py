def gameOfLife(board):
    m, n = len(board), len(board[0])
    res = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            live = 0
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = i + di, j + dj
                    if 0 <= ni < m and 0 <= nj < n and board[ni][nj] == 1:
                        live += 1
            if board[i][j] == 1:
                res[i][j] = 1 if live in (2, 3) else 0
            else:
                res[i][j] = 1 if live == 3 else 0
    return res
