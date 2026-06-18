def isSubsequence(s, t):
    it = iter(t)
    return all(c in it for c in s)
