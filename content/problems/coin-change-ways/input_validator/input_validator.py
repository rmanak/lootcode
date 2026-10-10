"""Input-constraint validator for problem 'coin-change-ways'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Hand-tightened: the generated check is kept as `_generated_validate_input`;
`validate_input` (bottom of file) adds the statement's input promises it
skipped. Do not overwrite this file with regenerated output; that drops them.
"""

def _generated_validate_input(amount, coins):
    if isinstance(amount, bool) or not isinstance(amount, int):
        return False
    if amount < 0 or amount > 5000:
        return False
    if not isinstance(coins, list):
        return False
    if len(coins) < 1 or len(coins) > 300:
        return False
    for x in coins:
        if isinstance(x, bool) or not isinstance(x, int) or x < 1 or x > 5000:
            return False
    return True


# --- Hand-added: statement promises the generated check skipped --------------
# The statement promises these about the input; they are checkable from the
# input alone, so they belong here (see docs/input-validators.md):
#   - `coins` are all distinct.

def _stated_promises(amount, coins):
    return len(set(coins)) == len(coins)


def validate_input(amount, coins):
    if not _generated_validate_input(amount, coins):
        return False
    try:
        return bool(_stated_promises(amount, coins))
    except Exception:  # malformed input the generated check let through
        return False
