def findReplaceString(S, indexes, sources, targets):
    ops = sorted(zip(indexes, sources, targets), reverse=True)
    s = S
    for i, src, tgt in ops:
        if s[i:i + len(src)] == src:
            s = s[:i] + tgt + s[i + len(src):]
    return s
