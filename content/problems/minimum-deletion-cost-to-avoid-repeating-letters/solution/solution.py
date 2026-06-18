def minCost(s, cost):
    total = 0
    i = 0
    n = len(s)
    while i < n:
        j = i
        run_sum = 0
        run_max = 0
        while j < n and s[j] == s[i]:
            run_sum += cost[j]
            run_max = max(run_max, cost[j])
            j += 1
        total += run_sum - run_max
        i = j
    return total
