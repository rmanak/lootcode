def minCost(costs):
    if not costs:
        return 0
    a, b, c = costs[0]
    for i in range(1, len(costs)):
        x, y, z = costs[i]
        a, b, c = x + min(b, c), y + min(a, c), z + min(a, b)
    return min(a, b, c)
