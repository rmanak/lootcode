def getHappyString(n, k):
    total = 3 * (2 ** (n - 1))
    if k > total:
        return ""
    res = []
    per = total
    prev = ""
    for pos in range(n):
        if pos == 0:
            choices = ['a', 'b', 'c']
            per //= 3
        else:
            choices = [c for c in 'abc' if c != prev]
            per //= 2
        idx = (k - 1) // per
        ch = choices[idx]
        res.append(ch)
        k -= idx * per
        prev = ch
    return "".join(res)
