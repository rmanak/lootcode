def subarrayBitwiseORs(arr):
    result = set()
    cur = set()
    for x in arr:
        cur = {x | y for y in cur} | {x}
        result |= cur
    return len(result)
