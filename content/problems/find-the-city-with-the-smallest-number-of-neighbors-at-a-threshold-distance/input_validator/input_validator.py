"""Input-constraint validator for problem 'find-the-city-with-the-smallest-number-of-neighbors-at-a-threshold-distance'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(n, edges, distanceThreshold):
    if isinstance(n, bool) or not isinstance(n, int):
        return False
    if n < 2 or n > 100:
        return False

    if not isinstance(edges, list):
        return False
    for edge in edges:
        if not isinstance(edge, list):
            return False
        if len(edge) != 3:
            return False
        a, b, w = edge
        if isinstance(a, bool) or not isinstance(a, int):
            return False
        if isinstance(b, bool) or not isinstance(b, int):
            return False
        if isinstance(w, bool) or not isinstance(w, int):
            return False
        if a < 0 or a >= b or b >= n:
            return False
        if w < 1 or w > 10000:
            return False

    if isinstance(distanceThreshold, bool) or not isinstance(distanceThreshold, int):
        return False
    if distanceThreshold < 1 or distanceThreshold > 10000:
        return False

    return True
