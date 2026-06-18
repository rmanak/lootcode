def longestRun(arr, queries):
    out = []
    for l, r in queries:
        best = cur = 1
        for i in range(l + 1, r + 1):
            cur = cur + 1 if arr[i] == arr[i - 1] else 1
            if cur > best:
                best = cur
        out.append(best)
    return out
