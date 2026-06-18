def runningAverage(nums):
    out = []
    s = 0
    for i, x in enumerate(nums):
        s += x
        out.append(round(s / (i + 1), 5))
    return out
