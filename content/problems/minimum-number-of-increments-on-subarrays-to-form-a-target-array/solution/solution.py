def minNumberOperations(target):
    res = target[0]
    for i in range(1, len(target)):
        if target[i] > target[i - 1]:
            res += target[i] - target[i - 1]
    return res
