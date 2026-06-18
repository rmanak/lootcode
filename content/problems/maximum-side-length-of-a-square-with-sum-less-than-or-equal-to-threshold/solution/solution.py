def maxSideLength(mat, threshold):
    m = len(mat)
    n = len(mat[0])
    pre = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            pre[i + 1][j + 1] = mat[i][j] + pre[i][j + 1] + pre[i + 1][j] - pre[i][j]

    def square_sum(r, c, k):
        return pre[r + k][c + k] - pre[r][c + k] - pre[r + k][c] + pre[r][c]

    best = 0
    k = 1
    while k <= min(m, n):
        found = False
        for i in range(m - k + 1):
            for j in range(n - k + 1):
                if square_sum(i, j, k) <= threshold:
                    found = True
                    break
            if found:
                break
        if found:
            best = k
            k += 1
        else:
            break
    return best
