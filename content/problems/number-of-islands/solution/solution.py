def numIslands(grid):
    if not grid or not grid[0]:
        return 0
    rows, cols = len(grid), len(grid[0])
    seen = [[False] * cols for _ in range(rows)]

    def flood(sr, sc):
        stack = [(sr, sc)]
        while stack:
            r, c = stack.pop()
            if 0 <= r < rows and 0 <= c < cols and not seen[r][c] and grid[r][c] == "1":
                seen[r][c] = True
                stack.extend([(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)])

    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and not seen[r][c]:
                flood(r, c)
                count += 1
    return count
