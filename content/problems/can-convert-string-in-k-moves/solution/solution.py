def canConvertString(s, t, k):
    if len(s) != len(t):
        return False
    from collections import defaultdict
    cnt = defaultdict(int)
    for a, b in zip(s, t):
        d = (ord(b) - ord(a)) % 26
        if d == 0:
            continue
        need = d + 26 * cnt[d]
        if need > k:
            return False
        cnt[d] += 1
    return True
