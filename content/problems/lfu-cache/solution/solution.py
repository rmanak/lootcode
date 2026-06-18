def lfuCache(capacity, operations):
    from collections import defaultdict, OrderedDict
    val, freq = {}, {}
    buckets = defaultdict(OrderedDict)
    minf = [0]
    out = []

    def bump(k):
        f = freq[k]
        del buckets[f][k]
        if not buckets[f]:
            del buckets[f]
            if minf[0] == f:
                minf[0] = f + 1
        freq[k] = f + 1
        buckets[f + 1][k] = None

    for op in operations:
        if op[0] == "get":
            k = op[1]
            if k in val:
                bump(k)
                out.append(val[k])
            else:
                out.append(-1)
        else:
            k, v = op[1], op[2]
            if capacity == 0:
                out.append(None)
                continue
            if k in val:
                val[k] = v
                bump(k)
            else:
                if len(val) >= capacity:
                    evk, _ = buckets[minf[0]].popitem(last=False)
                    del val[evk], freq[evk]
                val[k] = v
                freq[k] = 1
                buckets[1][k] = None
                minf[0] = 1
            out.append(None)
    return out
