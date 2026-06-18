def swapPairs(head):
    res = head[:]
    for i in range(0, len(res) - 1, 2):
        res[i], res[i + 1] = res[i + 1], res[i]
    return res
