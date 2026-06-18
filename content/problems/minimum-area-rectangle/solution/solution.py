def minAreaRect(points):
    pts = set(map(tuple, points))
    best = float("inf")
    P = [tuple(p) for p in points]
    for i in range(len(P)):
        x1, y1 = P[i]
        for j in range(i + 1, len(P)):
            x2, y2 = P[j]
            if x1 != x2 and y1 != y2 and (x1, y2) in pts and (x2, y1) in pts:
                area = abs(x1 - x2) * abs(y1 - y2)
                if area < best:
                    best = area
    return 0 if best == float("inf") else best
