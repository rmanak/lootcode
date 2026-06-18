def shortestBridge(grid):
    from collections import deque
    n, m = len(grid), len(grid[0])

    def nbrs(r, c):
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < m:
                yield nr, nc

    start = next((r, c) for r in range(n) for c in range(m) if grid[r][c] == 1)
    stack = [start]
    grid[start[0]][start[1]] = 2
    island = []
    while stack:
        r, c = stack.pop()
        island.append((r, c))
        for nr, nc in nbrs(r, c):
            if grid[nr][nc] == 1:
                grid[nr][nc] = 2
                stack.append((nr, nc))
    q = deque((r, c, 0) for r, c in island)
    seen = set(island)
    while q:
        r, c, d = q.popleft()
        for nr, nc in nbrs(r, c):
            if (nr, nc) in seen:
                continue
            if grid[nr][nc] == 1:
                return d
            seen.add((nr, nc))
            q.append((nr, nc, d + 1))
    return -1
