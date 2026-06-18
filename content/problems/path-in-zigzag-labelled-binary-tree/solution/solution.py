def pathInZigZagTree(label):
    path = []
    while label >= 1:
        path.append(label)
        L = label.bit_length()
        lo, hi = 1 << (L - 1), (1 << L) - 1
        label = (lo + hi - label) // 2
    return path[::-1]
