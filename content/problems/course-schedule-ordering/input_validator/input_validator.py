"""Input-constraint validator for problem 'course-schedule-ordering'.

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
    for pair in prerequisites:
        if not isinstance(pair, list):
            return False
        if len(pair) != 2:
            return False
        for x in pair:
            if isinstance(x, bool) or not isinstance(x, int):
                return False
            if x < 0 or x >= numCourses:
                return False
    return True
