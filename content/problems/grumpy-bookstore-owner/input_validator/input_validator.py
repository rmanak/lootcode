"""Input-constraint validator for problem 'grumpy-bookstore-owner'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(customers, grumpy, X):
    if not isinstance(customers, list) or not isinstance(grumpy, list):
        return False
    if isinstance(X, bool) or not isinstance(X, int):
        return False
        
    n = len(customers)
    if n < 1 or n > 20000:
        return False
    if len(grumpy) != n:
        return False
        
    if X < 1 or X > n:
        return False
        
    for x in customers:
        if isinstance(x, bool) or not isinstance(x, int) or x < 0 or x > 1000:
            return False
            
    for x in grumpy:
        if isinstance(x, bool) or not isinstance(x, int) or x not in (0, 1):
            return False
            
    return True
