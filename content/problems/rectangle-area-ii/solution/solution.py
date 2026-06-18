def rectangleArea(rectangles):
    MOD = 10 ** 9 + 7
    xs = sorted({r[0] for r in rectangles} | {r[2] for r in rectangles})
    total = 0
    for k in range(len(xs) - 1):
        x1, x2 = xs[k], xs[k + 1]
        width = x2 - x1
        if width == 0:
            continue
        spans = sorted((r[1], r[3]) for r in rectangles if r[0] <= x1 and r[2] >= x2)
        covered = 0
        cur_lo = cur_hi = None
        for lo, hi in spans:
            if cur_hi is None:
                cur_lo, cur_hi = lo, hi
            elif lo > cur_hi:
                covered += cur_hi - cur_lo
                cur_lo, cur_hi = lo, hi
            else:
                cur_hi = max(cur_hi, hi)
        if cur_hi is not None:
            covered += cur_hi - cur_lo
        total += width * covered
    return total % MOD
