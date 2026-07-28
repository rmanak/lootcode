"""Input-constraint validator for problem 'minimum-cost-to-travel'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Constraints deliberately NOT enforced:
  none -- every stated bound is a checkable property of the raw input.
"""


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def validate_input(target, capacity, position, price):
    if not _is_int(target) or not (1 <= target <= 10**9):
        return False
    if not _is_int(capacity) or not (1 <= capacity <= 10**9):
        return False
    if not isinstance(position, list) or not isinstance(price, list):
        return False
    m = len(position)
    if len(price) != m:
        return False
    if not (1 <= m <= 10**5):
        return False
    for p in price:
        if not _is_int(p) or not (1 <= p <= 10**9):
            return False
    prev = 0
    for d in position:
        if not _is_int(d):
            return False
        if not (prev < d < target):   # 0 < position[0] < ... < position[m-1] < target
            return False
        prev = d
    return True
