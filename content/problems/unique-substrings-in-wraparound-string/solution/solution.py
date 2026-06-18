def findSubstringInWraproundString(p):
    count = {}
    cur = 0
    for i, ch in enumerate(p):
        if i > 0 and (ord(ch) - ord(p[i - 1])) % 26 == 1:
            cur += 1
        else:
            cur = 1
        count[ch] = max(count.get(ch, 0), cur)
    return sum(count.values())
