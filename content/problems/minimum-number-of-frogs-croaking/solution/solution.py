def minNumberOfFrogs(croakOfFrogs):
    if len(croakOfFrogs) % 5 != 0:
        return -1
    c = r = o = a = k = 0
    max_frogs = 0
    for ch in croakOfFrogs:
        if ch == 'c':
            c += 1
            max_frogs = max(max_frogs, c - k)
        elif ch == 'r':
            r += 1
            if r > c:
                return -1
        elif ch == 'o':
            o += 1
            if o > r:
                return -1
        elif ch == 'a':
            a += 1
            if a > o:
                return -1
        elif ch == 'k':
            k += 1
            if k > a:
                return -1
    if c == r == o == a == k:
        return max_frogs
    return -1
