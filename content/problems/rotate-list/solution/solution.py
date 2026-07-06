def rotateRight(head, k):
    n = len(head)
    if n == 0:
        return []
    k %= n
    if k == 0:
        return head[:]
    return head[-k:] + head[:-k]
