def addTwoNumbers(l1, l2):
    res, carry, i = [], 0, 0
    while i < len(l1) or i < len(l2) or carry:
        d = carry
        if i < len(l1):
            d += l1[i]
        if i < len(l2):
            d += l2[i]
        res.append(d % 10)
        carry = d // 10
        i += 1
    return res
