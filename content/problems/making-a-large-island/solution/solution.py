def largestIsland(grid):
    from collections import deque
    g = [row[:] for row in grid]
    n, m = len(g), len(g[0])
    size = {}
    label = 2
    for i in range(n):
        for j in range(m):
            if g[i][j] == 1:
                dq = deque([(i, j)]); g[i][j] = label; cnt = 0
                while dq:
                    x, y = dq.popleft(); cnt += 1
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < n and 0 <= ny < m and g[nx][ny] == 1:
                            g[nx][ny] = label; dq.append((nx, ny))
                size[label] = cnt; label += 1
    best = max(size.values()) if size else 0
    for i in range(n):
        for j in range(m):
            if g[i][j] == 0:
                seen = set(); tot = 1
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = i + dx, j + dy
                    if 0 <= nx < n and 0 <= ny < m and g[nx][ny] > 1 and g[nx][ny] not in seen:
                        seen.add(g[nx][ny]); tot += size[g[nx][ny]]
                best = max(best, tot)
    return best
