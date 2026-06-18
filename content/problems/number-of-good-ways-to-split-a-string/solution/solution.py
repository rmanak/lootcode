def numSplits(s):
    n = len(s)
    left = [0] * n
    seen = set()
    for i, ch in enumerate(s):
        seen.add(ch)
        left[i] = len(seen)
    right = [0] * n
    seen = set()
    for i in range(n - 1, -1, -1):
        seen.add(s[i])
        right[i] = len(seen)
    return sum(1 for i in range(n - 1) if left[i] == right[i + 1])
