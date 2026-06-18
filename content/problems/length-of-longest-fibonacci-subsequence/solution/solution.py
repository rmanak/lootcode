def lenLongestFibSubseq(arr):
    idx = {x: i for i, x in enumerate(arr)}
    n = len(arr)
    dp = {}
    best = 0
    for j in range(n):
        for i in range(j):
            prev = arr[j] - arr[i]
            if prev < arr[i] and prev in idx:
                k = idx[prev]
                dp[(i, j)] = dp.get((k, i), 2) + 1
                best = max(best, dp[(i, j)])
    return best
