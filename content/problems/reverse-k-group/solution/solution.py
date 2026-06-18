def reverseKGroup(head, k):
    res, i, n = [], 0, len(head)
    while i + k <= n:
        res.extend(head[i:i + k][::-1])
        i += k
    res.extend(head[i:])
    return res
