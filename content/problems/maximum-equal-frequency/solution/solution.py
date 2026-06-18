def maxEqualFreq(nums):
    from collections import defaultdict
    count = defaultdict(int)
    freq = defaultdict(int)
    best = 0
    for i, x in enumerate(nums):
        count[x] += 1
        c = count[x]
        if c > 1:
            freq[c - 1] -= 1
            if freq[c - 1] == 0:
                del freq[c - 1]
        freq[c] += 1
        if len(freq) == 1:
            f = next(iter(freq))
            if f == 1 or freq[f] == 1:
                best = i + 1
        elif len(freq) == 2:
            lo, hi = sorted(freq)
            if (lo == 1 and freq[lo] == 1) or (hi == lo + 1 and freq[hi] == 1):
                best = i + 1
    return best
