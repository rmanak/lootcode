"""Input-constraint validator for problem 'equal-rational-numbers'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(S, T):
    if isinstance(S, bool) or not isinstance(S, str):
        return False
    if isinstance(T, bool) or not isinstance(T, str):
        return False

    def validate(s):
        if len(s) == 0:
            return False

        dot_idx = s.find('.')
        paren_idx = s.find('(')
        close_paren_idx = s.find(')')

        if dot_idx == -1:
            int_part = s
            if len(int_part) < 1 or len(int_part) > 4:
                return False
            if not int_part.isdigit():
                return False
            return True
        else:
            int_part = s[:dot_idx]
            if len(int_part) < 1 or len(int_part) > 4:
                return False
            if not int_part.isdigit():
                return False

            if paren_idx == -1:
                frac_part = s[dot_idx + 1:]
                if len(frac_part) > 4:
                    return False
                if len(frac_part) > 0 and not frac_part.isdigit():
                    return False
                return True
            else:
                if close_paren_idx == -1 or close_paren_idx != len(s) - 1:
                    return False
                if paren_idx < dot_idx:
                    return False
                frac_part = s[dot_idx + 1:paren_idx]
                repeat_part = s[paren_idx + 1:close_paren_idx]

                if len(frac_part) > 4:
                    return False
                if len(frac_part) > 0 and not frac_part.isdigit():
                    return False
                if len(repeat_part) < 1 or len(repeat_part) > 4:
                    return False
                if not repeat_part.isdigit():
                    return False
                return True

    return validate(S) and validate(T)
