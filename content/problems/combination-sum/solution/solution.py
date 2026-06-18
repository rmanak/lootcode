def combinationSum(candidates, target):
    candidates = sorted(candidates)
    res = []
    def bt(start, remain, path):
        if remain == 0:
            res.append(path[:])
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remain:
                break
            path.append(c)
            bt(i, remain - c, path)
            path.pop()
    bt(0, target, [])
    res.sort()
    return res
