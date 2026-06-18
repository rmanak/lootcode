def validSquare(p1, p2, p3, p4):
    pts = [p1, p2, p3, p4]

    def d2(a, b):
        return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

    dists = sorted(d2(pts[i], pts[j]) for i in range(4) for j in range(i + 1, 4))
    if dists[0] == 0:
        return False
    return (dists[0] == dists[1] == dists[2] == dists[3] and
            dists[4] == dists[5] and dists[4] == 2 * dists[0])
