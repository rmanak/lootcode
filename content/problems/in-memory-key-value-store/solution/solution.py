def kvStore(operations):
    store, snaps, out = {}, [], []
    for op in operations:
        name = op[0]
        if name == "set":
            store[op[1]] = op[2]
            out.append(None)
        elif name == "get":
            out.append(store.get(op[1]))
        elif name == "delete":
            store.pop(op[1], None)
            out.append(None)
        elif name == "snapshot":
            snaps.append(dict(store))
            out.append(len(snaps) - 1)
        else:
            k, sid = op[1], op[2]
            out.append(snaps[sid].get(k) if 0 <= sid < len(snaps) else None)
    return out
