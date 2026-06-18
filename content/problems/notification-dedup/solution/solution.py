def deduplicate(events, window):
    last = {}
    res = []
    for key, t in events:
        if key not in last or t - last[key] > window:
            res.append([key, t])
            last[key] = t
    return res
