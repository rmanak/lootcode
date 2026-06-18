def reverseBetween(head, m, n):
    a = head[:]
    a[m - 1:n] = a[m - 1:n][::-1]
    return a
