def majorityQueries(arr, queries):
    from collections import Counter
    res = []
    for left, right, threshold in queries:
        cnt = Counter(arr[left:right + 1])
        ans = -1
        for val, c in cnt.items():
            if c >= threshold:
                ans = val
                break
        res.append(ans)
    return res
