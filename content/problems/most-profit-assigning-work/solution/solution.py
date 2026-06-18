def maxProfitAssignment(difficulty, profit, worker):
    jobs = sorted(zip(difficulty, profit))
    worker = sorted(worker)
    i = 0
    best = 0
    total = 0
    for w in worker:
        while i < len(jobs) and jobs[i][0] <= w:
            best = max(best, jobs[i][1])
            i += 1
        total += best
    return total
