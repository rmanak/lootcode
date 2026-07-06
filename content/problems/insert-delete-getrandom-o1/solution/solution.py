def randomizedSet(operations):
    data = []
    pos = {}
    res = []
    for op in operations:
        name = op[0]
        if name == "RandomizedSet":
            data, pos = [], {}
            res.append(None)
        elif name == "insert":
            v = op[1]
            if v in pos:
                res.append(False)
            else:
                pos[v] = len(data)
                data.append(v)
                res.append(True)
        elif name == "remove":
            v = op[1]
            if v not in pos:
                res.append(False)
            else:
                i = pos[v]
                last = data[-1]
                data[i] = last
                pos[last] = i
                data.pop()
                del pos[v]
                res.append(True)
        elif name == "getRandom":
            res.append(data[0])
        else:
            raise ValueError(name)
    return res
