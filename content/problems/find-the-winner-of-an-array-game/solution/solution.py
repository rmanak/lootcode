def getWinner(arr, k):
    cur = arr[0]
    win = 0
    for i in range(1, len(arr)):
        if arr[i] > cur:
            cur = arr[i]
            win = 1
        else:
            win += 1
        if win == k:
            return cur
    return cur
