def largestNumber(nums):
    from functools import cmp_to_key
    arr = list(map(str, nums))
    arr.sort(key=cmp_to_key(lambda a, b: (a + b < b + a) - (a + b > b + a)))
    res = "".join(arr)
    return "0" if res[0] == '0' else res
