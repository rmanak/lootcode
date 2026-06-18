def regionsBySlashes(grid):
    n = len(grid)
    parent = list(range(4 * n * n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        parent[find(a)] = find(b)

    def idx(r, c, t):
        return 4 * (r * n + c) + t

    for r in range(n):
        for c in range(n):
            ch = grid[r][c]
            if ch == ' ':
                union(idx(r, c, 0), idx(r, c, 1))
                union(idx(r, c, 1), idx(r, c, 2))
                union(idx(r, c, 2), idx(r, c, 3))
            elif ch == '/':
                union(idx(r, c, 0), idx(r, c, 3))
                union(idx(r, c, 1), idx(r, c, 2))
            else:
                union(idx(r, c, 0), idx(r, c, 1))
                union(idx(r, c, 2), idx(r, c, 3))
            if r + 1 < n:
                union(idx(r, c, 2), idx(r + 1, c, 0))
            if c + 1 < n:
                union(idx(r, c, 1), idx(r, c + 1, 3))
    return sum(1 for i in range(4 * n * n) if find(i) == i)
