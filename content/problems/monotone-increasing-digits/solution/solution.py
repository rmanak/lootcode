def monotoneIncreasingDigits(N):
    digits = list(str(N))
    n = len(digits)
    mark = n
    for i in range(n - 1, 0, -1):
        if digits[i - 1] > digits[i]:
            digits[i - 1] = str(int(digits[i - 1]) - 1)
            mark = i
    for i in range(mark, n):
        digits[i] = '9'
    return int("".join(digits))
