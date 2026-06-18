def longestSubstring(s, k):
    if not s:
        return 0
    from collections import Counter
    cnt = Counter(s)
    for c in cnt:
        if cnt[c] < k:
            return max(longestSubstring(t, k) for t in s.split(c))
    return len(s)
