def minFlipsMonoIncr(S):
    ones = 0
    flips = 0
    for c in S:
        if c == '1':
            ones += 1
        else:
            flips = min(flips + 1, ones)
    return flips
