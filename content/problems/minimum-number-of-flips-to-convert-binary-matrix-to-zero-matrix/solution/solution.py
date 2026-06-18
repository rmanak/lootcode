def minFlips(mat):
    from collections import deque
    m, n = len(mat), len(mat[0])

    def encode(g):
        v = 0
        for i in range(m):
            for j in range(n):
                v = v * 2 + g[i][j]
        return v

    start = encode(mat)
    if start == 0:
        return 0

    masks = []
    for i in range(m):
        for j in range(n):
            bits = 0
            for di, dj in ((0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)):
                ni, nj = i + di, j + dj
                if 0 <= ni < m and 0 <= nj < n:
                    pos = ni * n + nj
                    bits ^= 1 << (m * n - 1 - pos)
            masks.append(bits)

    seen = {start}
    q = deque([(start, 0)])
    while q:
        s, d = q.popleft()
        for msk in masks:
            ns = s ^ msk
            if ns == 0:
                return d + 1
            if ns not in seen:
                seen.add(ns)
                q.append((ns, d + 1))
    return -1
