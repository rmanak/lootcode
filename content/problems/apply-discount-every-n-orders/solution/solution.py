def getBills(n, discount, products, prices, order_products, order_amounts):
    price = {p: prices[i] for i, p in enumerate(products)}
    res = []
    for c in range(len(order_products)):
        total = 0
        for pid, amt in zip(order_products[c], order_amounts[c]):
            total += price[pid] * amt
        if (c + 1) % n == 0:
            total = total - (discount * total) / 100
        res.append(round(float(total), 5))
    return res
