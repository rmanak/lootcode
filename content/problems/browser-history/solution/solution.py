def browserHistory(homepage, operations):
    hist = [homepage]
    cur = 0
    out = []
    for op in operations:
        if op[0] == "visit":
            hist = hist[:cur + 1]
            hist.append(op[1])
            cur = len(hist) - 1
            out.append(None)
        elif op[0] == "back":
            cur = max(0, cur - op[1])
            out.append(hist[cur])
        else:
            cur = min(len(hist) - 1, cur + op[1])
            out.append(hist[cur])
    return out
