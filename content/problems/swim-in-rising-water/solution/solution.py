def swimInWater(grid):
    import heapq
    n = len(grid)
    seen = [[False] * n for _ in range(n)]
    heap = [(grid[0][0], 0, 0)]
    seen[0][0] = True
    res = 0
    while heap:
        t, r, c = heapq.heappop(heap)
        res = max(res, t)
        if r == n - 1 and c == n - 1:
            return res
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and not seen[nr][nc]:
                seen[nr][nc] = True
                heapq.heappush(heap, (grid[nr][nc], nr, nc))
    return res
