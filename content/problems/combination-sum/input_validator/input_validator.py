"""Input-constraint validator for problem 'combination-sum'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Hand-tightened: the generated check is kept as `_generated_validate_input`;
`validate_input` (bottom of file) adds the statement's input promises it
skipped. Do not overwrite this file with regenerated output; that drops them.
"""

def _generated_validate_input(candidates, target):
    if not isinstance(candidates, list):
        return False
    if isinstance(target, bool) or not isinstance(target, int):
        return False
    if len(candidates) < 1 or len(candidates) > 30:
        return False
    if target < 1 or target > 40:
        return False
    for x in candidates:
        if isinstance(x, bool) or not isinstance(x, int) or x < 2 or x > 40:
            return False
    return True


# --- Hand-added: statement promises the generated check skipped --------------
# The statement promises these about the input; they are checkable from the
# input alone, so they belong here (see docs/input-validators.md):
#   - `candidates` are distinct.

def _stated_promises(candidates, target):
    return len(set(candidates)) == len(candidates)


def validate_input(candidates, target):
    if not _generated_validate_input(candidates, target):
        return False
    try:
        return bool(_stated_promises(candidates, target))
    except Exception:  # malformed input the generated check let through
        return False
