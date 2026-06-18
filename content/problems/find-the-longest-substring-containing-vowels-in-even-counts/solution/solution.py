def findTheLongestSubstring(s):
    vowels = {'a': 0, 'e': 1, 'i': 2, 'o': 3, 'u': 4}
    first = {0: -1}
    mask = 0
    best = 0
    for i, c in enumerate(s):
        if c in vowels:
            mask ^= 1 << vowels[c]
        if mask in first:
            best = max(best, i - first[mask])
        else:
            first[mask] = i
    return best
