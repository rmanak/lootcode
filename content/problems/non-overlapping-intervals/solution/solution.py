def eraseOverlapIntervals(intervals):
    intervals.sort(key=lambda x: x[1])
    removed = 0
    prev_end = float("-inf")
    for s, e in intervals:
        if s >= prev_end:
            prev_end = e
        else:
            removed += 1
    return removed
