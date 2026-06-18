def reserve(stock, requests):
    remaining = dict(stock)
    res = []
    for sku, qty in requests:
        have = remaining.get(sku, 0)
        if have >= qty:
            remaining[sku] = have - qty
            res.append(True)
        else:
            res.append(False)
    return res
