def findMinFibonacciNumbers(k):
    fibs = [1, 1]
    while fibs[-1] <= k:
        fibs.append(fibs[-1] + fibs[-2])
    count = 0
    i = len(fibs) - 1
    while k > 0:
        if fibs[i] <= k:
            k -= fibs[i]
            count += 1
        else:
            i -= 1
    return count
