def lruCache(capacity, operations):
    from collections import OrderedDict
    cache = OrderedDict()
    out = []
    for op in operations:
        if op[0] == "put":
            k, v = op[1], op[2]
            if k in cache:
                cache.move_to_end(k)
            cache[k] = v
            if len(cache) > capacity:
                cache.popitem(last=False)
            out.append(None)
        else:
            k = op[1]
            if k in cache:
                cache.move_to_end(k)
                out.append(cache[k])
            else:
                out.append(-1)
    return out
