def alertNames(keyName, keyTime):
    from collections import defaultdict
    times = defaultdict(list)
    for name, t in zip(keyName, keyTime):
        h, m = t.split(':')
        times[name].append(int(h) * 60 + int(m))
    res = []
    for name, ts in times.items():
        ts.sort()
        for i in range(2, len(ts)):
            if ts[i] - ts[i - 2] <= 60:
                res.append(name)
                break
    return sorted(res)
