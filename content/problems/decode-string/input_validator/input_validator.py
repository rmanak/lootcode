"""Input-constraint validator for problem 'decode-string'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""


def validate_input(s):
    if not isinstance(s, str):
        return False
    if len(s) < 1 or len(s) > 30:
        return False
    # The input follows the k[encoded_string] format:
    # - letters (a-z) and digits (1-9) are allowed
    # - '[' and ']' are allowed as encoding delimiters
    if not all(c.isalpha() or c.isdigit() or c in '[]' for c in s):
        return False
    # Brackets must be balanced
    depth = 0
    for c in s:
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
        if depth < 0:
            return False
    if depth != 0:
        return False
    # Digits only appear as repeat counts (k is a positive integer before '[')
    # Every '[' must be preceded by a positive integer (>=1)
    i = 0
    while i < len(s):
        if s[i].isalpha():
            # Consume consecutive letters
            while i < len(s) and s[i].isalpha():
                i += 1
        elif s[i].isdigit():
            # Must be a repeat count — consume full number
            num_start = i
            while i < len(s) and s[i].isdigit():
                i += 1
            num = int(s[num_start:i])
            # Must be followed by '[' and must be positive
            if i >= len(s) or s[i] != '[':
                return False
            if num < 1:
                return False
            i += 1  # skip past '['
        elif s[i] == '[':
            return False  # '[' without preceding number
        elif s[i] == ']':
            i += 1
        else:
            return False
    return True
