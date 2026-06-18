def maxUniqueSplit(s):
    n = len(s)
    best = [0]

    def bt(start, seen):
        if start == n:
            best[0] = max(best[0], len(seen))
            return
        if len(seen) + (n - start) <= best[0]:
            return
        for end in range(start + 1, n + 1):
            sub = s[start:end]
            if sub not in seen:
                seen.add(sub)
                bt(end, seen)
                seen.remove(sub)

    bt(0, set())
    return best[0]
