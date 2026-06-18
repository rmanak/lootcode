def getStrongest(arr, k):
    s = sorted(arr)
    m = s[(len(s) - 1) // 2]
    s.sort(key=lambda x: (abs(x - m), x), reverse=True)
    return s[:k]
