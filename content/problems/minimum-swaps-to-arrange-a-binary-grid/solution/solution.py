def minSwaps(grid):
    n = len(grid)
    zeros = []
    for row in grid:
        c = 0
        for x in reversed(row):
            if x == 0:
                c += 1
            else:
                break
        zeros.append(c)
    res = 0
    for i in range(n):
        need = n - 1 - i
        j = i
        while j < n and zeros[j] < need:
            j += 1
        if j == n:
            return -1
        while j > i:
            zeros[j], zeros[j - 1] = zeros[j - 1], zeros[j]
            res += 1
            j -= 1
    return res
