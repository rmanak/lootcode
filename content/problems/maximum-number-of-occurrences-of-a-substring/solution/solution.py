def maxFreq(s, maxLetters, minSize, maxSize):
    from collections import Counter
    cnt = Counter()
    n = len(s)
    for i in range(n - minSize + 1):
        sub = s[i:i + minSize]
        if len(set(sub)) <= maxLetters:
            cnt[sub] += 1
    return max(cnt.values()) if cnt else 0
