def totalNQueens(n):
    count = [0]
    cols = set()
    diag = set()
    anti = set()

    def dfs(r):
        if r == n:
            count[0] += 1
            return
        for c in range(n):
            if c in cols or (r - c) in diag or (r + c) in anti:
                continue
            cols.add(c)
            diag.add(r - c)
            anti.add(r + c)
            dfs(r + 1)
            cols.discard(c)
            diag.discard(r - c)
            anti.discard(r + c)

    dfs(0)
    return count[0]
