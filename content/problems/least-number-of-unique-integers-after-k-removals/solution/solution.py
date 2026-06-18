def findLeastNumOfUniqueInts(arr, k):
    from collections import Counter
    counts = sorted(Counter(arr).values())
    for i, c in enumerate(counts):
        if k >= c:
            k -= c
        else:
            return len(counts) - i
    return 0
