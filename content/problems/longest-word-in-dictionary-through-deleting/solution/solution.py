def findLongestWord(s, d):
    def is_sub(w):
        it = iter(s)
        return all(c in it for c in w)
    best = ""
    for w in d:
        if is_sub(w) and (len(w) > len(best) or (len(w) == len(best) and w < best)):
            best = w
    return best
