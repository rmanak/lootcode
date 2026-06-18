def deleteDuplicates(head):
    res = []
    i, n = 0, len(head)
    while i < n:
        j = i
        while j < n and head[j] == head[i]:
            j += 1
        if j - i == 1:
            res.append(head[i])
        i = j
    return res
