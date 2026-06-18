def jobScheduling(start, end, profit):
    import bisect
    jobs = sorted(zip(end, start, profit))
    ends = [j[0] for j in jobs]
    n = len(jobs)
    res = [0] * (n + 1)
    for i in range(1, n + 1):
        e, s, p = jobs[i - 1]
        idx = bisect.bisect_right(ends, s)
        res[i] = max(res[i - 1], p + res[idx])
    return res[n]
