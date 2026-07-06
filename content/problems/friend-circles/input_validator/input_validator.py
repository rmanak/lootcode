"""Input-constraint validator for problem 'friend-circles'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(M):
    if not isinstance(M, list):
        return False
    n = len(M)
    if n < 1 or n > 200:
        return False
    for row in M:
        if not isinstance(row, list):
            return False
        if len(row) != n:
            return False
        for x in row:
            if isinstance(x, bool) or not isinstance(x, int):
                return False
            if x != 0 and x != 1:
                return False
    for i in range(n):
        if M[i][i] != 1:
            return False
    for i in range(n):
        for j in range(n):
            if M[i][j] != M[j][i]:
                return False
    return True
