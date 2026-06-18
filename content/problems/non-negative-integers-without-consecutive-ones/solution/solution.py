def findIntegers(n):
    fib = [1, 2]
    for i in range(2, 32):
        fib.append(fib[-1] + fib[-2])
    res = 0
    prev_bit = 0
    for i in range(30, -1, -1):
        if (n >> i) & 1:
            res += fib[i]
            if prev_bit == 1:
                return res
            prev_bit = 1
        else:
            prev_bit = 0
    return res + 1
