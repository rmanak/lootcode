def rateLimiter(limit, window, operations):
    from collections import defaultdict, deque
    hist = defaultdict(deque)
    out = []
    for op in operations:
        _, user, t = op
        dq = hist[user]
        while dq and dq[0] <= t - window:
            dq.popleft()
        if len(dq) < limit:
            dq.append(t)
            out.append(True)
        else:
            out.append(False)
    return out
