def minMeetingRooms(intervals):
    starts = sorted(s for s, _ in intervals)
    ends = sorted(e for _, e in intervals)
    rooms = best = 0
    j = 0
    for s in starts:
        while j < len(ends) and ends[j] <= s:
            j += 1
            rooms -= 1
        rooms += 1
        best = max(best, rooms)
    return best
