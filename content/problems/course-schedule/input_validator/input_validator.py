"""Input-constraint validator for problem 'course-schedule'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(numCourses, prerequisites):
    if isinstance(numCourses, bool) or not isinstance(numCourses, int):
        return False
    if numCourses < 1 or numCourses > 2000:
        return False
    if not isinstance(prerequisites, list):
        return False
    if len(prerequisites) < 0 or len(prerequisites) > 5000:
        return False
    seen = set()
    for pair in prerequisites:
        if not isinstance(pair, list):
            return False
        if len(pair) != 2:
            return False
        a, b = pair[0], pair[1]
        if isinstance(a, bool) or not isinstance(a, int):
            return False
        if isinstance(b, bool) or not isinstance(b, int):
            return False
        if a < 0 or a >= numCourses:
            return False
        if b < 0 or b >= numCourses:
            return False
        if (a, b) in seen:
            return False
        seen.add((a, b))
    return True
