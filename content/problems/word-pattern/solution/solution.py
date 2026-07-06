def wordPattern(pattern, s):
    words = s.split()
    if len(pattern) != len(words):
        return False
    pw, wp = {}, {}
    for c, w in zip(pattern, words):
        if c in pw and pw[c] != w:
            return False
        if w in wp and wp[w] != c:
            return False
        pw[c] = w
        wp[w] = c
    return True
