def balancedString(s):
    from collections import Counter
    n = len(s)
    need = n // 4
    cnt = Counter(s)
    if all(cnt[c] == need for c in "QWER"):
        return 0
    res = n
    l = 0
    for r in range(n):
        cnt[s[r]] -= 1
        while l <= r and all(cnt[c] <= need for c in "QWER"):
            res = min(res, r - l + 1)
            cnt[s[l]] += 1
            l += 1
    return res
