def partition(head, x):
    less = [v for v in head if v < x]
    ge = [v for v in head if v >= x]
    return less + ge
