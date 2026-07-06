def findSubstring(s, words):
    from collections import Counter
    if not words or not s:
        return []
    wlen = len(words[0])
    k = len(words)
    total = wlen * k
    if total > len(s):
        return []
    need = Counter(words)
    res = []
    for i in range(len(s) - total + 1):
        seen = Counter()
        j = i
        ok = True
        for _ in range(k):
            w = s[j:j + wlen]
            if need[w] == 0:
                ok = False
                break
            seen[w] += 1
            if seen[w] > need[w]:
                ok = False
                break
            j += wlen
        if ok:
            res.append(i)
    return res
