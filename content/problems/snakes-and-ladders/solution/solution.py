def snakesAndLadders(board):
    from collections import deque
    n = len(board)
    target = n * n
    def cell(label):
        idx = label - 1
        r, c = divmod(idx, n)
        if r % 2 == 1:
            c = n - 1 - c
        return n - 1 - r, c
    dist = {1: 0}
    q = deque([1])
    while q:
        cur = q.popleft()
        for d in range(1, 7):
            nxt = cur + d
            if nxt > target:
                break
            r, c = cell(nxt)
            if board[r][c] != -1:
                nxt = board[r][c]
            if nxt == target:
                return dist[cur] + 1
            if nxt not in dist:
                dist[nxt] = dist[cur] + 1
                q.append(nxt)
    return 0 if n * n == 1 else -1
