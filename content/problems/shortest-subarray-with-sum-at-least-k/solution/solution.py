def shortestSubarray(A, K):
    from collections import deque
    n = len(A)
    pre = [0] * (n + 1)
    for i in range(n):
        pre[i + 1] = pre[i] + A[i]
    dq = deque()
    res = n + 1
    for i in range(n + 1):
        while dq and pre[i] - pre[dq[0]] >= K:
            res = min(res, i - dq.popleft())
        while dq and pre[dq[-1]] >= pre[i]:
            dq.pop()
        dq.append(i)
    return res if res <= n else -1
