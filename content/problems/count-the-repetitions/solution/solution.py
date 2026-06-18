def getMaxRepetitions(s1, n1, s2, n2):
    if n1 == 0:
        return 0
    len2 = len(s2)
    s2cnt = [0] * len2
    nxt = [0] * len2
    for i in range(len2):
        cnt, idx = 0, i
        for ch in s1:
            if ch == s2[idx]:
                idx += 1
                if idx == len2:
                    idx = 0
                    cnt += 1
        s2cnt[i] = cnt
        nxt[i] = idx
    total, idx = 0, 0
    for _ in range(n1):
        total += s2cnt[idx]
        idx = nxt[idx]
    return total // n2
