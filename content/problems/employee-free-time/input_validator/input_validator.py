"""Input-constraint validator for problem 'employee-free-time'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Hand-tightened: the generated check is kept as `_generated_validate_input`;
`validate_input` (bottom of file) adds the statement's input promises it
skipped. Do not overwrite this file with regenerated output; that drops them.
"""

def _generated_validate_input(schedule):
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


# --- Hand-added: statement promises the generated check skipped --------------
# The statement promises these about the input; they are checkable from the
# input alone, so they belong here (see docs/input-validators.md):
#   - Each employee's intervals are non-overlapping and sorted by start.

def _stated_promises(schedule):
    for emp in schedule:
        for (s1, e1), (s2, e2) in zip(emp, emp[1:]):
            if s2 < e1:
                return False
    return True


def validate_input(schedule):
    if not _generated_validate_input(schedule):
        return False
    try:
        return bool(_stated_promises(schedule))
    except Exception:  # malformed input the generated check let through
        return False
