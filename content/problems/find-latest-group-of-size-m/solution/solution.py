def findLatestStep(arr, m):
    n = len(arr)
    length = [0] * (n + 2)
    count = [0] * (n + 1)
    res = -1
    for step, pos in enumerate(arr, 1):
        left = length[pos - 1]
        right = length[pos + 1]
        new_len = left + right + 1
        length[pos - left] = new_len
        length[pos + right] = new_len
        if left > 0:
            count[left] -= 1
        if right > 0:
            count[right] -= 1
        count[new_len] += 1
        if count[m] > 0:
            res = step
    return res
