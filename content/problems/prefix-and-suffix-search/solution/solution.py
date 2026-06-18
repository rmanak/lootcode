def wordFilter(words, queries):
    res = []
    for prefix, suffix in queries:
        ans = -1
        for i in range(len(words) - 1, -1, -1):
            if words[i].startswith(prefix) and words[i].endswith(suffix):
                ans = i
                break
        res.append(ans)
    return res
