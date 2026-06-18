def shortestPathAllKeys(grid):
    from collections import deque
    R, C = len(grid), len(grid[0])
    start = None
    total = 0
    for i in range(R):
        for j in range(C):
            ch = grid[i][j]
            if ch == '@':
                start = (i, j)
            elif ch.islower():
                total += 1
    full = (1 << total) - 1
    q = deque([(start[0], start[1], 0, 0)])
    seen = {(start[0], start[1], 0)}
    while q:
        r, c, keys, d = q.popleft()
        if keys == full:
            return d
        for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C:
                ch = grid[nr][nc]
                if ch == '#':
                    continue
                if ch.isupper() and not (keys >> (ord(ch) - ord('A')) & 1):
                    continue
                nk = keys
                if ch.islower():
                    nk = keys | (1 << (ord(ch) - ord('a')))
                if (nr, nc, nk) not in seen:
                    seen.add((nr, nc, nk))
                    q.append((nr, nc, nk, d + 1))
    return -1
