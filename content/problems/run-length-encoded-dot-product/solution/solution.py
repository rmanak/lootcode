def rleDot(a, b):
    total = 0
    i = j = 0
    left_a, left_b = a[0][1], b[0][1]     # unused part of the current run in each vector
    while i < len(a) and j < len(b):
        step = min(left_a, left_b)
        total += a[i][0] * b[j][0] * step
        left_a -= step
        left_b -= step
        if left_a == 0:
            i += 1
            if i < len(a):
                left_a = a[i][1]
        if left_b == 0:
            j += 1
            if j < len(b):
                left_b = b[j][1]
    return total
