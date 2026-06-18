def maximumSum(arr):
    n = len(arr)
    no_del = arr[0]
    one_del = float('-inf')
    best = arr[0]
    for i in range(1, n):
        one_del = max(no_del, one_del + arr[i])
        no_del = max(arr[i], no_del + arr[i])
        best = max(best, no_del, one_del)
    return best
