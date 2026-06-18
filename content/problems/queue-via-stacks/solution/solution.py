def myQueue(operations):
    inn, out_s, out = [], [], []
    for op in operations:
        if op[0] == "push":
            inn.append(op[1])
            out.append(None)
        elif op[0] == "pop":
            if not out_s:
                while inn:
                    out_s.append(inn.pop())
            out.append(out_s.pop())
        elif op[0] == "peek":
            if not out_s:
                while inn:
                    out_s.append(inn.pop())
            out.append(out_s[-1])
        else:
            out.append(len(inn) == 0 and len(out_s) == 0)
    return out
