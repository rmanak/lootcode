from collections import deque


def canReachWithinBudget(grid, nMoves, nRemove):
    m, n = len(grid), len(grid[0])
    target = m + n - 2
    if target == 0:
        return True
    if nMoves < target:
        return False
    # The edge path visits m + n - 2 cells after the start (target included),
    # so with that many removals it is always open.
    if nRemove >= target:
        return True

    # BFS over (row, col, removals left), layer by layer in move count.
    # best[r][c] = most removals left on any earlier (shorter) arrival at (r, c);
    # an arrival that is no shorter and no richer than that one is dominated.
    best = [[-1] * n for _ in range(m)]
    best[0][0] = nRemove
    queue = deque([(0, 0, nRemove)])
    moves = 0
    while queue and moves < nMoves:
        moves += 1
        for _ in range(len(queue)):
            r, c, left = queue.popleft()
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < m and 0 <= nc < n:
                    nleft = left - grid[nr][nc]
                    if nleft > best[nr][nc]:
                        if nr == m - 1 and nc == n - 1:
                            return True
                        best[nr][nc] = nleft
                        queue.append((nr, nc, nleft))
    return False
