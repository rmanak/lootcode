"""Input-constraint validator for problem 'add-two-numbers'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Hand-tightened: the generated check is kept as `_generated_validate_input`;
`validate_input` (bottom of file) adds the statement's input promises it
skipped. Do not overwrite this file with regenerated output; that drops them.
"""

def _generated_validate_input(l1, l2):
    if not isinstance(l1, list) or not isinstance(l2, list):
        return False
    if len(l1) < 1 or len(l1) > 100:
        return False
    if len(l2) < 1 or len(l2) > 100:
        return False
    for x in l1:
        if isinstance(x, bool) or not isinstance(x, int) or x < 0 or x > 9:
            return False
    for x in l2:
        if isinstance(x, bool) or not isinstance(x, int) or x < 0 or x > 9:
            return False
    return True


# --- Hand-added: statement promises the generated check skipped --------------
# The statement promises these about the input; they are checkable from the
# input alone, so they belong here (see docs/input-validators.md):
#   - Each number has no leading zero except `0` itself (digits are stored in
#     reverse, so the last node is the most significant).

def _stated_promises(l1, l2):
    return all(l == [0] or l[-1] != 0 for l in (l1, l2))


def validate_input(l1, l2):
    if not _generated_validate_input(l1, l2):
        return False
    try:
        return bool(_stated_promises(l1, l2))
    except Exception:  # malformed input the generated check let through
        return False
