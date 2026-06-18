def shiftingLetters(S, shifts):
    n = len(S)
    res = [''] * n
    suffix = 0
    for i in range(n - 1, -1, -1):
        suffix = (suffix + shifts[i]) % 26
        res[i] = chr(97 + (ord(S[i]) - 97 + suffix) % 26)
    return "".join(res)
