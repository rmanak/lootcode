def shortestPathBinaryMatrix(grid):
    from collections import deque
    n = len(grid)
    if grid[0][0] != 0 or grid[n - 1][n - 1] != 0:
        return -1
    q = deque([(0, 0, 1)])
    seen = {(0, 0)}
    while q:
        x, y, d = q.popleft()
        if x == n - 1 and y == n - 1:
            return d
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < n and 0 <= ny < n and grid[nx][ny] == 0                         and (nx, ny) not in seen:
                    seen.add((nx, ny))
                    q.append((nx, ny, d + 1))
    return -1
