def minimumMoves(grid):
    from collections import deque
    n = len(grid)
    start = (0, 0, 0)            # row, col, orientation (0 horizontal, 1 vertical)
    target = (n - 1, n - 2, 0)
    seen = {start}
    dq = deque([(start, 0)])
    while dq:
        (r, c, o), d = dq.popleft()
        if (r, c, o) == target:
            return d
        nxts = []
        if o == 0:  # horizontal: cells (r,c),(r,c+1)
            if c + 2 < n and grid[r][c + 2] == 0:
                nxts.append((r, c + 1, 0))
            if r + 1 < n and grid[r + 1][c] == 0 and grid[r + 1][c + 1] == 0:
                nxts.append((r + 1, c, 0))
                nxts.append((r, c, 1))
        else:       # vertical: cells (r,c),(r+1,c)
            if c + 1 < n and grid[r][c + 1] == 0 and grid[r + 1][c + 1] == 0:
                nxts.append((r, c + 1, 1))
                nxts.append((r, c, 0))
            if r + 2 < n and grid[r + 2][c] == 0:
                nxts.append((r + 1, c, 1))
        for st in nxts:
            if st not in seen:
                seen.add(st); dq.append((st, d + 1))
    return -1
