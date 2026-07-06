def combine(n, k):
    from itertools import combinations
    return [list(c) for c in combinations(range(1, n + 1), k)]
