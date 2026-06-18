def multipartComplete(parts, expected):
    present = set()
    total = 0
    for pn, b in parts:
        present.add(pn)
        total += b
    complete = all(i in present for i in range(1, expected + 1))
    return [complete, total]
