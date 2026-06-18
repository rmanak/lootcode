def maxDistToClosest(seats):
    n = len(seats)
    prev = -1
    best = 0
    for i in range(n):
        if seats[i] == 1:
            if prev == -1:
                best = i
            else:
                best = max(best, (i - prev) // 2)
            prev = i
    best = max(best, n - 1 - prev)
    return best
