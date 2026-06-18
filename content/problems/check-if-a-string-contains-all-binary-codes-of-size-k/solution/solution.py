def hasAllCodes(s, k):
    if len(s) < k:
        return False
    seen = set()
    for i in range(len(s) - k + 1):
        seen.add(s[i:i + k])
    return len(seen) == (1 << k)
