def removeNthFromEnd(head, n):
    idx = len(head) - n
    return head[:idx] + head[idx + 1:]
