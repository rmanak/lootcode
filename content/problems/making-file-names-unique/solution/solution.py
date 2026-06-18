def getFolderNames(names):
    seen = {}
    res = []
    for name in names:
        if name not in seen:
            seen[name] = 1
            res.append(name)
        else:
            k = seen[name]
            while f"{name}({k})" in seen:
                k += 1
            new = f"{name}({k})"
            seen[name] = k + 1
            seen[new] = 1
            res.append(new)
    return res
