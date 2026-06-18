def minSteps(s, t):
    from collections import Counter
    cs = Counter(s)
    ct = Counter(t)
    return sum((ct - cs).values())
