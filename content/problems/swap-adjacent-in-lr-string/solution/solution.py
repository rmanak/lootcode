def canTransform(start, end):
    if len(start) != len(end):
        return False
    if start.replace('X', '') != end.replace('X', ''):
        return False
    s = [(c, i) for i, c in enumerate(start) if c != 'X']
    e = [(c, i) for i, c in enumerate(end) if c != 'X']
    for (c, i), (_, j) in zip(s, e):
        if c == 'L' and i < j:
            return False
        if c == 'R' and i > j:
            return False
    return True
