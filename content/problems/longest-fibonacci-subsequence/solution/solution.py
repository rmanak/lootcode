def lenLongestFibSubseq(arr):
    idx = {v: i for i, v in enumerate(arr)}
    n = len(arr)
    dp = {}
    best = 0
    for j in range(n):
        for k in range(j + 1, n):
            i = idx.get(arr[k] - arr[j])
            if i is not None and i < j:
                dp[(j, k)] = dp.get((i, j), 2) + 1
                best = max(best, dp[(j, k)])
    return best if best >= 3 else 0
