def canConstruct(s, k):
    from collections import Counter
    if len(s) < k:
        return False
    odd = sum(v % 2 for v in Counter(s).values())
    return odd <= k
