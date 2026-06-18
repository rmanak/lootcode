def getProbability(balls):
    from math import comb
    k = len(balls)
    n = sum(balls) // 2
    fav = [0]
    den = [0]

    def rec(i, left, d1, d2, ways):
        if i == k:
            if left == 0:
                den[0] += ways
                if d1 == d2:
                    fav[0] += ways
            return
        for a in range(0, balls[i] + 1):
            if a > left:
                break
            rec(i + 1, left - a, d1 + (1 if a > 0 else 0),
                d2 + (1 if balls[i] - a > 0 else 0), ways * comb(balls[i], a))

    rec(0, n, 0, 0, 1)
    return round(fav[0] / den[0], 5)
