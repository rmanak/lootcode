def compactLog(samples):
    out = []
    for t, s in samples:
        if out and out[-1][2] == s:
            out[-1][1] = t
        else:
            out.append([t, t, s])
    return out
