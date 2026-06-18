def checkInclusion(s1, s2):
    from collections import Counter
    need = Counter(s1)
    k = len(s1)
    if k > len(s2):
        return False
    window = Counter(s2[:k])
    if window == need:
        return True
    for i in range(k, len(s2)):
        window[s2[i]] += 1
        window[s2[i - k]] -= 1
        if window[s2[i - k]] == 0:
            del window[s2[i - k]]
        if window == need:
            return True
    return False
