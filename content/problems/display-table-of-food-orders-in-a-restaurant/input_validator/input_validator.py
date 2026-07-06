"""Input-constraint validator for problem 'display-table-of-food-orders-in-a-restaurant'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(orders):
    if not isinstance(orders, list):
        return False
    if len(orders) < 1 or len(orders) > 50000:
        return False
    for order in orders:
        if not isinstance(order, list):
            return False
        if len(order) != 3:
            return False
        for item in order:
            if not isinstance(item, str):
                return False
        try:
            table_num = int(order[1])
        except (ValueError, TypeError):
            return False
        if table_num < 1 or table_num > 500:
            return False
    return True
