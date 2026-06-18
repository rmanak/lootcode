def minCut(s):
    n = len(s)
    pal = [[False] * n for _ in range(n)]
    for i in range(n):
        pal[i][i] = True
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j] and (length == 2 or pal[i + 1][j - 1]):
                pal[i][j] = True
    cuts = [0] * n
    for i in range(n):
        if pal[0][i]:
            cuts[i] = 0
        else:
            cuts[i] = min(cuts[k - 1] + 1 for k in range(1, i + 1) if pal[k][i])
    return cuts[n - 1]
