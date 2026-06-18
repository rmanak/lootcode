def threeSumMulti(A, target):
    MOD = 10 ** 9 + 7
    from collections import Counter
    cnt = Counter(A)
    keys = sorted(cnt)
    res = 0
    nk = len(keys)
    for i in range(nk):
        for j in range(i, nk):
            x, y = keys[i], keys[j]
            z = target - x - y
            if z < y or z not in cnt:
                continue
            cz = cnt[z]
            if x == y == z:
                c = cnt[x]
                res += c * (c - 1) * (c - 2) // 6
            elif x == y != z:
                c = cnt[x]
                res += c * (c - 1) // 2 * cz
            elif x != y == z:
                c = cnt[y]
                res += cnt[x] * (c * (c - 1) // 2)
            else:
                res += cnt[x] * cnt[y] * cz
    return res % MOD
