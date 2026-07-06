def maxPoints(points):
    from math import gcd
    n = len(points)
    if n <= 2:
        return n
    best = 1
    for i in range(n):
        slopes = {}
        for j in range(n):
            if i == j:
                continue
            dx = points[j][0] - points[i][0]
            dy = points[j][1] - points[i][1]
            g = gcd(dx, dy)
            if g:
                dx //= g
                dy //= g
            if dx < 0 or (dx == 0 and dy < 0):
                dx, dy = -dx, -dy
            slopes[(dx, dy)] = slopes.get((dx, dy), 0) + 1
            best = max(best, slopes[(dx, dy)] + 1)
    return best
