def totalFruit(tree):
    from collections import defaultdict
    count = defaultdict(int)
    l = 0
    best = 0
    for r, t in enumerate(tree):
        count[t] += 1
        while len(count) > 2:
            count[tree[l]] -= 1
            if count[tree[l]] == 0:
                del count[tree[l]]
            l += 1
        best = max(best, r - l + 1)
    return best
