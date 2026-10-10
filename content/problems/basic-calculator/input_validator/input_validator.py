"""Input-constraint validator for problem 'basic-calculator'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Beyond the character set, this checks the string is a *grammatically valid*
expression: balanced parentheses, `-` used as binary subtraction except that a
unary `-` may appear only immediately after `(` (the one place the statement
permits it). A charset-only gate wrongly accepted ungrammatical strings like
`-2--6`, which would let a suite (or the fuzzer/shrinker) bake the canonical's
behavior on illegal input and unfairly fail a solution written to the contract.
Spaces are ignored, matching the canonical evaluator.

Hand-tightened: the generated check is kept as `_generated_validate_input`;
`validate_input` (bottom of file) adds the statement's input promises it
skipped. Do not overwrite this file with regenerated output; that drops them.
"""

def _generated_validate_input(s):
    if not isinstance(s, str):
        return False
    if len(s) < 1 or len(s) > 300000:
        return False
    if any(c not in "0123456789+-() " for c in s):
        return False
    t = s.replace(" ", "")      # the canonical ignores spaces entirely
    if not t:
        return False
    pos = 0

    def parse_expr(allow_unary):
        nonlocal pos
        if not parse_term(allow_unary):
            return False
        while pos < len(t) and t[pos] in "+-":
            pos += 1
            if not parse_term(False):   # after a binary operator, no unary sign
                return False
        return True

    def parse_term(allow_unary):
        nonlocal pos
        if allow_unary and pos < len(t) and t[pos] == "-":
            pos += 1                    # unary minus, only at a group/expr start
        if pos < len(t) and t[pos] == "(":
            pos += 1
            if not parse_expr(True):    # `-` may follow `(`
                return False
            if pos >= len(t) or t[pos] != ")":
                return False
            pos += 1
            return True
        if pos >= len(t) or not t[pos].isdigit():
            return False
        while pos < len(t) and t[pos].isdigit():
            pos += 1
        return True

    try:
        return parse_expr(False) and pos == len(t)
    except RecursionError:
        return False


# --- Hand-added: statement promises the generated check skipped --------------
# The statement promises these about the input; they are checkable from the
# input alone, so they belong here (see docs/input-validators.md):
#   - `s` is a valid expression of digits, `+`, `-`, `(`, `)` and spaces; `-`
#     is binary, except that it may directly follow `(`.

import re


def _stated_promises(s):
    if re.search(r"[^0-9+\-() ]", s):
        return False
    toks = re.findall(r"\d+|[-+()]", s)
    i, depth = 0, 0
    expect_operand = True
    prev = None
    for t in toks:
        if expect_operand:
            if t.isdigit():
                expect_operand = False
            elif t == "(":
                depth += 1
            elif t == "-" and prev == "(":
                pass                      # unary minus right after "("
            else:
                return False
        else:
            if t in "+-":
                expect_operand = True
            elif t == ")" and depth > 0:
                depth -= 1
            else:
                return False
        prev = t
    return bool(toks) and not expect_operand and depth == 0


def validate_input(s):
    if not _generated_validate_input(s):
        return False
    try:
        return bool(_stated_promises(s))
    except Exception:  # malformed input the generated check let through
        return False
