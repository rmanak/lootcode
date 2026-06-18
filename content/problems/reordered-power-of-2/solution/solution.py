def reorderedPowerOf2(N):
    from collections import Counter
    target = Counter(str(N))
    return any(Counter(str(1 << i)) == target for i in range(31))
