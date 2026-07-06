"""Input-constraint validator for problem 'apply-discount-every-n-orders'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(n, discount, products, prices, order_products, order_amounts):
    if isinstance(n, bool) or not isinstance(n, int):
        return False
    if n < 1 or n > 10000:
        return False

    if isinstance(discount, bool) or not isinstance(discount, int):
        return False
    if discount < 0 or discount > 100:
        return False

    if not isinstance(products, list):
        return False
    for x in products:
        if isinstance(x, bool) or not isinstance(x, int):
            return False
    if len(products) != len(set(products)):
        return False

    if not isinstance(prices, list):
        return False
    if len(prices) != len(products):
        return False
    for x in prices:
        if isinstance(x, bool) or not isinstance(x, int):
            return False
        if x < 1 or x > 1000:
            return False

    if not isinstance(order_products, list):
        return False
    product_set = set(products)
    for row in order_products:
        if not isinstance(row, list):
            return False
        for x in row:
            if isinstance(x, bool) or not isinstance(x, int):
                return False
            if x not in product_set:
                return False

    if not isinstance(order_amounts, list):
        return False
    if len(order_amounts) != len(order_products):
        return False
    for i in range(len(order_amounts)):
        row = order_amounts[i]
        if not isinstance(row, list):
            return False
        if len(row) != len(order_products[i]):
            return False
        for x in row:
            if isinstance(x, bool) or not isinstance(x, int):
                return False
            if x < 1 or x > 1000:
                return False

    return True
