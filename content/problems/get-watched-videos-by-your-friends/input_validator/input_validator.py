"""Input-constraint validator for problem 'get-watched-videos-by-your-friends'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(watchedVideos, friends, id, level):
    if not isinstance(watchedVideos, list):
        return False
    if not isinstance(friends, list):
        return False
    if isinstance(id, bool) or not isinstance(id, int):
        return False
    if isinstance(level, bool) or not isinstance(level, int):
        return False

    n = len(watchedVideos)
    if n < 2 or n > 100:
        return False
    if len(friends) != n:
        return False

    if id < 0 or id >= n:
        return False
    if level < 1 or level >= n:
        return False

    for i in range(n):
        if not isinstance(watchedVideos[i], list):
            return False
        for v in watchedVideos[i]:
            if not isinstance(v, str):
                return False

    for i in range(n):
        if not isinstance(friends[i], list):
            return False
        for f in friends[i]:
            if isinstance(f, bool) or not isinstance(f, int):
                return False
            if f < 0 or f >= n:
                return False

    for i in range(n):
        for f in friends[i]:
            if i not in friends[f]:
                return False

    return True
