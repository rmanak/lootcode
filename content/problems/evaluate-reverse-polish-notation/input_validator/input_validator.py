"""Input-constraint validator for problem 'evaluate-reverse-polish-notation'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Hand-tightened: the generated check is kept as `_generated_validate_input`;
`validate_input` (bottom of file) adds the statement's input promises it
skipped. Do not overwrite this file with regenerated output; that drops them.
"""

def _generated_validate_input(tokens):
    if not isinstance(tokens, list):
        return False
    if len(tokens) < 1 or len(tokens) > 10000:
        return False
    for t in tokens:
        if not isinstance(t, str):
            return False
        if t in ('+', '-', '*', '/'):
            continue
        try:
            val = int(t)
        except ValueError:
            return False
        if val < -20000 or val > 20000:
            return False
    return True


# --- Hand-added: statement promises the generated check skipped --------------
# The statement promises these about the input; they are checkable from the
# input alone, so they belong here (see docs/input-validators.md):
#   - The expression is always valid: every operator has two operands, exactly
#     one value remains, and no division is by zero.
#   - Each operand and intermediate result fits in a signed 64-bit integer.

def _stated_promises(tokens):
    stack = []
    for t in tokens:
        if t in ("+", "-", "*", "/"):
            if len(stack) < 2:
                return False
            b, a = stack.pop(), stack.pop()
            if t == "/" and b == 0:
                return False
            if t == "+":
                v = a + b
            elif t == "-":
                v = a - b
            elif t == "*":
                v = a * b
            else:
                v = abs(a) // abs(b) * (1 if (a < 0) == (b < 0) else -1)
            if not -2**63 <= v < 2**63:
                return False
            stack.append(v)
        else:
            stack.append(int(t))
    return len(stack) == 1


def validate_input(tokens):
    if not _generated_validate_input(tokens):
        return False
    try:
        return bool(_stated_promises(tokens))
    except Exception:  # malformed input the generated check let through
        return False
