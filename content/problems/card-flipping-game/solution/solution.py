def flipgame(fronts, backs):
    same = {f for f, b in zip(fronts, backs) if f == b}
    best = float('inf')
    for x in fronts + backs:
        if x not in same:
            best = min(best, x)
    return best if best != float('inf') else 0
