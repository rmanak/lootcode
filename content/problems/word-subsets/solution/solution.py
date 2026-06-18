def wordSubsets(A, B):
    from collections import Counter
    need = Counter()
    for b in B:
        for ch, k in Counter(b).items():
            need[ch] = max(need[ch], k)
    res = []
    for a in A:
        ac = Counter(a)
        if all(ac[ch] >= k for ch, k in need.items()):
            res.append(a)
    return res
