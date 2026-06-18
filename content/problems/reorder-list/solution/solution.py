def reorderList(head):
    res = []
    i, j = 0, len(head) - 1
    while i <= j:
        res.append(head[i])
        if i != j:
            res.append(head[j])
        i += 1
        j -= 1
    return res
