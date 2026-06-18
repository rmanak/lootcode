def maxArea(h, w, horizontalCuts, verticalCuts):
    MOD = 10 ** 9 + 7
    hc = sorted(horizontalCuts)
    vc = sorted(verticalCuts)
    max_h = max(hc[0], h - hc[-1])
    for i in range(1, len(hc)):
        max_h = max(max_h, hc[i] - hc[i - 1])
    max_v = max(vc[0], w - vc[-1])
    for i in range(1, len(vc)):
        max_v = max(max_v, vc[i] - vc[i - 1])
    return (max_h * max_v) % MOD
