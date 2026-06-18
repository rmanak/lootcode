def shortestPalindrome(s):
    if not s:
        return s
    rev = s[::-1]
    combined = s + "#" + rev
    n = len(combined)
    lps = [0] * n
    for i in range(1, n):
        j = lps[i - 1]
        while j > 0 and combined[i] != combined[j]:
            j = lps[j - 1]
        if combined[i] == combined[j]:
            j += 1
        lps[i] = j
    overlap = lps[-1]
    return rev[:len(s) - overlap] + s
