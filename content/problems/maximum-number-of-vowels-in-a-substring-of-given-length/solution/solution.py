def maxVowels(s, k):
    vowels = set('aeiou')
    cur = sum(1 for c in s[:k] if c in vowels)
    best = cur
    for i in range(k, len(s)):
        cur += (s[i] in vowels) - (s[i - k] in vowels)
        best = max(best, cur)
    return best
