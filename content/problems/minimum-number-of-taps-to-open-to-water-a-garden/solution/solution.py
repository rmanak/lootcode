def minTaps(n, ranges):
    max_reach = [0] * (n + 1)
    for i, r in enumerate(ranges):
        left = max(0, i - r)
        right = min(n, i + r)
        max_reach[left] = max(max_reach[left], right)
    taps = 0
    cur_end = 0
    next_end = 0
    i = 0
    while cur_end < n:
        while i <= cur_end:
            next_end = max(next_end, max_reach[i])
            i += 1
        if next_end <= cur_end:
            return -1
        cur_end = next_end
        taps += 1
    return taps
