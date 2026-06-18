def xorQueries(arr, queries):
    pre = [0]
    for x in arr:
        pre.append(pre[-1] ^ x)
    return [pre[r + 1] ^ pre[l] for l, r in queries]
