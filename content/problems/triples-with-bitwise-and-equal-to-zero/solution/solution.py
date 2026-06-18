def countTriplets(A):
    from collections import Counter
    pair = Counter()
    for x in A:
        for y in A:
            pair[x & y] += 1
    res = 0
    for x in A:
        for v, c in pair.items():
            if x & v == 0:
                res += c
    return res
