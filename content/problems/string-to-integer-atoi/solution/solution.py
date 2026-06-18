def myAtoi(s):
    i, n = 0, len(s)
    while i < n and s[i] == ' ':
        i += 1
    sign = 1
    if i < n and s[i] in '+-':
        if s[i] == '-':
            sign = -1
        i += 1
    num = 0
    while i < n and s[i].isdigit():
        num = num * 10 + int(s[i])
        i += 1
    num *= sign
    INT_MIN, INT_MAX = -2 ** 31, 2 ** 31 - 1
    return max(INT_MIN, min(INT_MAX, num))
