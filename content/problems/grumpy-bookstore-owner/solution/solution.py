def maxSatisfied(customers, grumpy, X):
    n = len(customers)
    base = sum(customers[i] for i in range(n) if grumpy[i] == 0)
    extra = 0
    best = 0
    for i in range(n):
        if grumpy[i] == 1:
            extra += customers[i]
        if i >= X and grumpy[i - X] == 1:
            extra -= customers[i - X]
        best = max(best, extra)
    return base + best
