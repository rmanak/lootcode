def minInteger(num, k):
    n = len(num)
    from collections import deque
    pos = [deque() for _ in range(10)]
    for i, c in enumerate(num):
        pos[int(c)].append(i)
    bit = [0] * (n + 1)

    def update(i):
        i += 1
        while i <= n:
            bit[i] += 1
            i += i & -i

    def query(i):
        i += 1
        s = 0
        while i > 0:
            s += bit[i]
            i -= i & -i
        return s

    res = []
    for _ in range(n):
        for d in range(10):
            if pos[d]:
                idx = pos[d][0]
                removed_before = query(idx - 1) if idx > 0 else 0
                cost = idx - removed_before
                if cost <= k:
                    k -= cost
                    res.append(str(d))
                    pos[d].popleft()
                    update(idx)
                    break
    return "".join(res)
