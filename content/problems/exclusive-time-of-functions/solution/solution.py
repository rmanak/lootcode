def exclusiveTime(n, logs):
    res = [0] * n
    stack = []
    prev = 0
    for log in logs:
        fid_s, typ, ts_s = log.split(':')
        fid, ts = int(fid_s), int(ts_s)
        if typ == 'start':
            if stack:
                res[stack[-1]] += ts - prev
            stack.append(fid)
            prev = ts
        else:
            res[stack.pop()] += ts - prev + 1
            prev = ts + 1
    return res
