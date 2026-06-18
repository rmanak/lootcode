def maxIncreaseKeepingSkyline(grid):
    rows = [max(r) for r in grid]
    cols = [max(c) for c in zip(*grid)]
    total = 0
    for i, r in enumerate(grid):
        for j, v in enumerate(r):
            total += min(rows[i], cols[j]) - v
    return total
