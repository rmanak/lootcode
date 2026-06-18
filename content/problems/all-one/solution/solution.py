def allOne(operations):
    count = {}
    out = []
    for op in operations:
        if op[0] == "inc":
            count[op[1]] = count.get(op[1], 0) + 1
            out.append(None)
        elif op[0] == "dec":
            k = op[1]
            count[k] -= 1
            if count[k] == 0:
                del count[k]
            out.append(None)
        elif op[0] == "getMaxKey":
            if not count:
                out.append("")
            else:
                mx = max(count.values())
                out.append(min(k for k, v in count.items() if v == mx))
        else:
            if not count:
                out.append("")
            else:
                mn = min(count.values())
                out.append(min(k for k, v in count.items() if v == mn))
    return out
