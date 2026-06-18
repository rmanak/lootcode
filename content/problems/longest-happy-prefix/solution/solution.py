def longestPrefix(s):
    n = len(s)
    lps = [0] * n
    k = 0
    for i in range(1, n):
        while k > 0 and s[i] != s[k]:
            k = lps[k - 1]
        if s[i] == s[k]:
            k += 1
        lps[i] = k
    return s[:lps[n - 1]]
