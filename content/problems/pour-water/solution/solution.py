def pourWater(heights, V, K):
    h = heights[:]
    n = len(h)
    for _ in range(V):
        best = K
        i = K
        while i - 1 >= 0 and h[i - 1] <= h[i]:
            i -= 1
            if h[i] < h[best]:
                best = i
        if best != K:
            h[best] += 1
            continue
        i = K
        while i + 1 < n and h[i + 1] <= h[i]:
            i += 1
            if h[i] < h[best]:
                best = i
        h[best] += 1
    return h
