def reverseKGroup(head, k):
    res = []
    n = len(head)
    i = 0
    while i + k <= n:
        res.extend(head[i:i + k][::-1])
        i += k
    res.extend(head[i:])
    return res
