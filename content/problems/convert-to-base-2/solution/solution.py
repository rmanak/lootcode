def baseNeg2(N):
    if N == 0:
        return "0"
    digits = []
    while N != 0:
        r = N % (-2)
        N //= (-2)
        if r < 0:
            r += 2
            N += 1
        digits.append(str(r))
    return "".join(reversed(digits))
