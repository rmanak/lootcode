def solve(board):
    if not board or not board[0]:
        return board
    from collections import deque
    m, n = len(board), len(board[0])
    board = [row[:] for row in board]
    q = deque()
    for r in range(m):
        for c in range(n):
            if (r in (0, m - 1) or c in (0, n - 1)) and board[r][c] == "O":
                board[r][c] = "#"
                q.append((r, c))
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and board[nr][nc] == "O":
                board[nr][nc] = "#"
                q.append((nr, nc))
    for r in range(m):
        for c in range(n):
            board[r][c] = "O" if board[r][c] == "#" else "X"
    return board
