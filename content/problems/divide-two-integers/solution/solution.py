def divide(dividend, divisor):
    INT_MAX, INT_MIN = 2 ** 31 - 1, -2 ** 31
    if dividend == INT_MIN and divisor == -1:
        return INT_MAX
    neg = (dividend < 0) != (divisor < 0)
    a, b = abs(dividend), abs(divisor)
    q = 0
    while a >= b:
        temp, m = b, 1
        while a >= (temp << 1):
            temp <<= 1
            m <<= 1
        a -= temp
        q += m
    q = -q if neg else q
    return max(INT_MIN, min(INT_MAX, q))
