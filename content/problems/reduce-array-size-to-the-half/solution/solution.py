def minSetSize(arr):
    from collections import Counter
    counts = sorted(Counter(arr).values(), reverse=True)
    removed = 0
    res = 0
    half = len(arr) / 2
    for c in counts:
        removed += c
        res += 1
        if removed >= half:
            break
    return res
