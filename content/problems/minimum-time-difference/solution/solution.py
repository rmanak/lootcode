def findMinDifference(timePoints):
    mins = sorted(int(t[:2]) * 60 + int(t[3:]) for t in timePoints)
    if len(mins) > 1440:
        return 0
    best = min(b - a for a, b in zip(mins, mins[1:]))
    return min(best, 1440 - mins[-1] + mins[0])
