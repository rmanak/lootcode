def minFallingPathSumII(arr):
    n = len(arr)
    prev = arr[0][:]
    for i in range(1, n):
        m1 = m2 = None
        i1 = -1
        for j, v in enumerate(prev):
            if m1 is None or v < m1:
                m2 = m1; m1 = v; i1 = j
            elif m2 is None or v < m2:
                m2 = v
        cur = []
        for j in range(n):
            cur.append(arr[i][j] + (m2 if j == i1 else m1))
        prev = cur
    return min(prev)
