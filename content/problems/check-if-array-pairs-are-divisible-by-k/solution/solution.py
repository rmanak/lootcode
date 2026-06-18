def canArrange(arr, k):
    from collections import Counter
    cnt = Counter(x % k for x in arr)
    for r in range(k):
        if r == 0:
            if cnt[0] % 2:
                return False
        elif cnt[r] != cnt[k - r]:
            return False
    return True
