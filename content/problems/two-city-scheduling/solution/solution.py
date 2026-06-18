def twoCitySchedCost(costs):
    costs = sorted(costs, key=lambda c: c[0] - c[1])
    n = len(costs) // 2
    return sum((c[0] if i < n else c[1]) for i, c in enumerate(costs))
