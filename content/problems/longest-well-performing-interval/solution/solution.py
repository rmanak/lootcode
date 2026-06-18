def longestWPI(hours):
    score = 0
    best = 0
    seen = {}
    for i, h in enumerate(hours):
        score += 1 if h > 8 else -1
        if score > 0:
            best = i + 1
        elif score - 1 in seen:
            best = max(best, i - seen[score - 1])
        if score not in seen:
            seen[score] = i
    return best
