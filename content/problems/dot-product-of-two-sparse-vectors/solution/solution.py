from bisect import bisect_left


def sparseDot(a, b):
    if len(a) > len(b):
        a, b = b, a
    if len(a) * 20 < len(b):
        # Very unbalanced: binary-search each short entry in the long list.
        idx = [p[0] for p in b]
        total, lo = 0, 0
        for i, v in a:
            lo = bisect_left(idx, i, lo)
            if lo == len(idx):
                break
            if idx[lo] == i:
                total += v * b[lo][1]
        return total
    total, p, q = 0, 0, 0
    while p < len(a) and q < len(b):
        if a[p][0] == b[q][0]:
            total += a[p][1] * b[q][1]
            p += 1
            q += 1
        elif a[p][0] < b[q][0]:
            p += 1
        else:
            q += 1
    return total
