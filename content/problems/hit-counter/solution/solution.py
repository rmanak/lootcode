def hitCounter(operations):
    from collections import deque
    hits = deque()
    out = []
    for op in operations:
        if op[0] == "hit":
            hits.append(op[1])
            out.append(None)
        else:
            t = op[1]
            while hits and hits[0] <= t - 300:
                hits.popleft()
            out.append(len(hits))
    return out
