def contiguousOffset(processed):
    s = set(processed)
    i = 0
    while i in s:
        i += 1
    return i - 1
