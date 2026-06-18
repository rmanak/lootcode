def closestDivisors(num):
    import math
    best = None
    for target in (num + 1, num + 2):
        a = int(math.isqrt(target))
        while target % a != 0:
            a -= 1
        pair = [a, target // a]
        if best is None or (pair[1] - pair[0]) < (best[1] - best[0]):
            best = pair
    return best
