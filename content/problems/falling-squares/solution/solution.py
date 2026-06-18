def fallingSquares(positions):
    n = len(positions)
    heights = [0] * n
    res = []
    best = 0
    for i, (l, s) in enumerate(positions):
        r = l + s
        base = 0
        for j in range(i):
            lj, sj = positions[j]
            if l < lj + sj and lj < r:
                base = max(base, heights[j])
        heights[i] = base + s
        best = max(best, heights[i])
        res.append(best)
    return res
