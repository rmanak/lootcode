def frequencySort(s):
    from collections import Counter
    cnt = Counter(s)
    chars = sorted(cnt, key=lambda c: (-cnt[c], c))
    return "".join(c * cnt[c] for c in chars)
