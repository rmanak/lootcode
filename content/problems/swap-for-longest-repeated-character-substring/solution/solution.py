def maxRepOpt1(text):
    from collections import Counter
    cnt = Counter(text)
    groups = []
    i = 0
    n = len(text)
    while i < n:
        j = i
        while j < n and text[j] == text[i]:
            j += 1
        groups.append((text[i], j - i))
        i = j
    res = 0
    for ch, length in groups:
        res = max(res, min(length + 1, cnt[ch]))
    for i in range(1, len(groups) - 1):
        if groups[i - 1][0] == groups[i + 1][0] and groups[i][1] == 1:
            ch = groups[i - 1][0]
            total = groups[i - 1][1] + groups[i + 1][1]
            res = max(res, min(total + 1, cnt[ch]))
    return res
