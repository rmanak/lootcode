def largest1BorderedSquare(grid):
    m, n = len(grid), len(grid[0])
    hor = [[0] * n for _ in range(m)]
    ver = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1:
                hor[i][j] = (hor[i][j - 1] if j > 0 else 0) + 1
                ver[i][j] = (ver[i - 1][j] if i > 0 else 0) + 1
    best = 0
    for i in range(m):
        for j in range(n):
            side = min(hor[i][j], ver[i][j])
            while side > best:
                if ver[i][j - side + 1] >= side and hor[i - side + 1][j] >= side:
                    best = side
                    break
                side -= 1
    return best * best
