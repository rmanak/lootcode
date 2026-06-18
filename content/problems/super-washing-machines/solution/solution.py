def findMinMoves(machines):
    total = sum(machines)
    n = len(machines)
    if total % n != 0:
        return -1
    avg = total // n
    res = 0
    running = 0
    for m in machines:
        diff = m - avg
        running += diff
        res = max(res, abs(running), diff)
    return res
