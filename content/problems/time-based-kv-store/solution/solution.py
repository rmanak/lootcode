def timeMap(operations):
    import bisect
    from collections import defaultdict
    times = defaultdict(list)
    vals = defaultdict(list)
    out = []
    for op in operations:
        if op[0] == "set":
            _, key, value, ts = op
            times[key].append(ts)
            vals[key].append(value)
            out.append(None)
        else:
            _, key, ts = op
            arr = times[key]
            i = bisect.bisect_right(arr, ts)
            out.append(vals[key][i - 1] if i > 0 else "")
    return out
