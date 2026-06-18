def numOfSubarrays(arr, k, threshold):
    target = k * threshold
    s = sum(arr[:k])
    cnt = 1 if s >= target else 0
    for i in range(k, len(arr)):
        s += arr[i] - arr[i - k]
        if s >= target:
            cnt += 1
    return cnt
