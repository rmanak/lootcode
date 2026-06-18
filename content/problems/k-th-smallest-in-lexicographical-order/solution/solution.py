def findKthNumber(n, k):
    def count(prefix):
        cnt = 0
        cur, nxt = prefix, prefix + 1
        while cur <= n:
            cnt += min(n + 1, nxt) - cur
            cur *= 10
            nxt *= 10
        return cnt

    cur = 1
    k -= 1
    while k > 0:
        c = count(cur)
        if c <= k:
            k -= c
            cur += 1
        else:
            cur *= 10
            k -= 1
    return cur
