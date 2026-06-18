def checkIfCanBreak(s1, s2):
    a = sorted(s1)
    b = sorted(s2)
    le = all(a[i] <= b[i] for i in range(len(a)))
    ge = all(a[i] >= b[i] for i in range(len(a)))
    return le or ge
