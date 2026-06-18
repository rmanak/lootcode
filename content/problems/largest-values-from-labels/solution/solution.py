def largestValsFromLabels(values, labels, numWanted, useLimit):
    from collections import defaultdict
    items = sorted(zip(values, labels), reverse=True)
    used = defaultdict(int)
    total = 0
    count = 0
    for v, l in items:
        if count >= numWanted:
            break
        if used[l] < useLimit:
            total += v
            used[l] += 1
            count += 1
    return total
