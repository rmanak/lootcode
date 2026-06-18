def canReorderDoubled(arr):
    from collections import Counter
    cnt = Counter(arr)
    for x in sorted(arr, key=abs):
        if cnt[x] == 0:
            continue
        if cnt[2 * x] == 0:
            return False
        cnt[x] -= 1
        cnt[2 * x] -= 1
    return True
