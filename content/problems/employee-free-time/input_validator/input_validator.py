"""Input-constraint validator for problem 'employee-free-time'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(schedule):
    if not isinstance(schedule, list):
        return False
    if len(schedule) < 1 or len(schedule) > 100:
        return False
    for employee in schedule:
        if not isinstance(employee, list):
            return False
        if len(employee) < 1 or len(employee) > 100:
            return False
        for interval in employee:
            if not isinstance(interval, list):
                return False
            if len(interval) != 2:
                return False
            start, end = interval
            if isinstance(start, bool) or not isinstance(start, int):
                return False
            if isinstance(end, bool) or not isinstance(end, int):
                return False
            if start < 0 or start >= end or end > 1000000000:
                return False
    return True
