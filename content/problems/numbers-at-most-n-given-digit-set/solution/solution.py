def atMostNGivenDigitSet(digits, n):
    s = str(n)
    L = len(s)
    D = len(digits)
    res = 0
    for i in range(1, L):
        res += D ** i
    ds = digits
    for i, ch in enumerate(s):
        res += sum(1 for d in ds if d < ch) * (D ** (L - i - 1))
        if ch not in ds:
            break
    else:
        res += 1
    return res
