def kSimilarity(A, B):
    from collections import deque
    if A == B:
        return 0
    n = len(A)

    def neighbors(s):
        i = 0
        while s[i] == B[i]:
            i += 1
        res = []
        for j in range(i + 1, n):
            if s[j] == B[i] and s[j] != B[j]:
                res.append(s[:i] + s[j] + s[i + 1:j] + s[i] + s[j + 1:])
        return res

    seen = {A}
    dq = deque([(A, 0)])
    while dq:
        cur, k = dq.popleft()
        if cur == B:
            return k
        for nb in neighbors(cur):
            if nb not in seen:
                seen.add(nb)
                dq.append((nb, k + 1))
    return -1
