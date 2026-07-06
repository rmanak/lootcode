"""Input-constraint validator for problem 'count-unhappy-friends'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(n, preferences, pairs):
    if isinstance(n, bool) or not isinstance(n, int):
        return False
    if n < 2 or n > 500:
        return False
    if n % 2 != 0:
        return False

    if not isinstance(preferences, list):
        return False
    if len(preferences) != n:
        return False

    for i in range(n):
        if not isinstance(preferences[i], list):
            return False
        if len(preferences[i]) != n - 1:
            return False
        seen = set()
        for x in preferences[i]:
            if isinstance(x, bool) or not isinstance(x, int):
                return False
            if x < 0 or x >= n:
                return False
            if x == i:
                return False
            if x in seen:
                return False
            seen.add(x)
        if len(seen) != n - 1:
            return False

    if not isinstance(pairs, list):
        return False
    if len(pairs) != n // 2:
        return False

    seen_friends = set()
    for pair in pairs:
        if not isinstance(pair, list):
            return False
        if len(pair) != 2:
            return False
        if pair[0] == pair[1]:
            return False
        for x in pair:
            if isinstance(x, bool) or not isinstance(x, int):
                return False
            if x < 0 or x >= n:
                return False
            if x in seen_friends:
                return False
            seen_friends.add(x)

    if len(seen_friends) != n:
        return False

    return True
