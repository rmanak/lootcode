def getSum(a, b):
    mask = 0xFFFFFFFF
    a &= mask
    b &= mask
    while b:
        carry = ((a & b) << 1) & mask
        a = (a ^ b) & mask
        b = carry
    return a if a <= 0x7FFFFFFF else a - 0x100000000
