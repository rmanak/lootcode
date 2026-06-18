def hashRing(operations):
    import bisect
    servers, out = [], []
    for op in operations:
        name = op[0]
        if name == "addServer":
            i = bisect.bisect_left(servers, op[1])
            if i == len(servers) or servers[i] != op[1]:
                servers.insert(i, op[1])
            out.append(None)
        elif name == "removeServer":
            i = bisect.bisect_left(servers, op[1])
            if i < len(servers) and servers[i] == op[1]:
                servers.pop(i)
            out.append(None)
        else:
            key = op[1]
            if not servers:
                out.append(None)
            else:
                i = bisect.bisect_left(servers, key)
                out.append(servers[i] if i < len(servers) else servers[0])
    return out
