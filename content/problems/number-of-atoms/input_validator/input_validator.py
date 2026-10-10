"""Input-constraint validator for problem 'number-of-atoms'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Hand-written: enforces "a valid formula": elements are an uppercase letter plus
lowercase letters, counts (no leading zero) follow only an element or ")", and
parentheses are balanced and non-empty.
The generated version skipped this as a "semantic guarantee", which let the
retired test generator bake in a malformed hidden case. Do not regenerate.
"""
_ALLOWED = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz()0123456789")


def validate_input(formula):
    if not isinstance(formula, str):
        return False
    if not (1 <= len(formula) <= 1000):
        return False
    if not set(formula) <= _ALLOWED:
        return False
    nonempty = [False]          # one flag per open group: has it any content yet?
    prev = None                 # kind of the previous token
    i, n = 0, len(formula)
    while i < n:
        c = formula[i]
        if c.isupper():
            i += 1
            while i < n and formula[i].islower():
                i += 1
            nonempty[-1] = True
            prev = "elem"
            continue
        if c == "(":
            nonempty.append(False)
            prev = "open"
        elif c == ")":
            if len(nonempty) == 1 or not nonempty[-1]:
                return False
            nonempty.pop()
            nonempty[-1] = True
            prev = "close"
        elif c.isdigit():
            if prev not in ("elem", "close") or c == "0":
                return False
            while i + 1 < n and formula[i + 1].isdigit():
                i += 1
            prev = "count"
        else:                   # a lowercase letter not continuing an element
            return False
        i += 1
    return len(nonempty) == 1 and nonempty[0]
