"""Input-constraint validator for problem 'find-and-replace-in-string'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(S, indexes, sources, targets):
    if not isinstance(S, str):
        return False
    if not isinstance(indexes, list):
        return False
    if not isinstance(sources, list):
        return False
    if not isinstance(targets, list):
        return False

    if len(indexes) < 0 or len(indexes) > 100:
        return False

    if len(indexes) != len(sources) or len(indexes) != len(targets):
        return False

    for x in indexes:
        if isinstance(x, bool) or not isinstance(x, int):
            return False
        if x < 0 or x >= len(S):
            return False

    for x in sources:
        if not isinstance(x, str):
            return False
        for c in x:
            if not ('a' <= c <= 'z'):
                return False

    for x in targets:
        if not isinstance(x, str):
            return False
        for c in x:
            if not ('a' <= c <= 'z'):
                return False

    for c in S:
        if not ('a' <= c <= 'z'):
            return False

    return True
