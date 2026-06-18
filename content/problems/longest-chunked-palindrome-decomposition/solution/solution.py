def longestDecomposition(text):
    res = 0
    l, r = 0, len(text)
    while l < r:
        for k in range(1, (r - l) // 2 + 1):
            if text[l:l + k] == text[r - k:r]:
                res += 2
                l += k
                r -= k
                break
        else:
            res += 1
            break
    return res
