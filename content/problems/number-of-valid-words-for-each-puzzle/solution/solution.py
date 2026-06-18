def findNumOfValidWords(words, puzzles):
    from collections import Counter
    cnt = Counter()
    for w in words:
        mask = 0
        for c in set(w):
            mask |= 1 << (ord(c) - 97)
        cnt[mask] += 1
    res = []
    for p in puzzles:
        first = 1 << (ord(p[0]) - 97)
        pmask = 0
        for c in p:
            pmask |= 1 << (ord(c) - 97)
        total = 0
        sub = pmask
        while sub:
            if sub & first:
                total += cnt.get(sub, 0)
            sub = (sub - 1) & pmask
        res.append(total)
    return res
