def findOriginalArray(changed):
    from collections import Counter
    if len(changed) % 2 != 0:
        return []
    cnt = Counter(changed)
    res = []
    for x in sorted(changed):
        if cnt[x] == 0:
            continue
        if x == 0:
            if cnt[0] < 2:
                return []
            cnt[0] -= 2
            res.append(0)
        else:
            cnt[x] -= 1
            if cnt[2 * x] <= 0:
                return []
            cnt[2 * x] -= 1
            res.append(x)
    return sorted(res)
