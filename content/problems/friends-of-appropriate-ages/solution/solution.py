def numFriendRequests(ages):
    from collections import Counter
    cnt = Counter(ages)
    res = 0
    for a in cnt:
        for b in cnt:
            if b <= 0.5 * a + 7 or b > a or (b > 100 and a < 100):
                continue
            res += cnt[a] * cnt[b] - (cnt[a] if a == b else 0)
    return res
