def equalSubstring(s, t, maxCost):
    l = 0
    cost = 0
    best = 0
    for r in range(len(s)):
        cost += abs(ord(s[r]) - ord(t[r]))
        while cost > maxCost:
            cost -= abs(ord(s[l]) - ord(t[l]))
            l += 1
        best = max(best, r - l + 1)
    return best
