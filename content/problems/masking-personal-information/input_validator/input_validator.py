"""Input-constraint validator for problem 'masking-personal-information'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Hand-written: enforces "a valid email or phone number": an email is
name1@name2.name3 (letters only); a phone is digits plus "+-() " with 10-13 digits.
The generated version skipped this as a "semantic guarantee", which let the
retired test generator bake in a malformed hidden case. Do not regenerate.
"""
import re

_EMAIL = re.compile(r"[A-Za-z]+@[A-Za-z]+\.[A-Za-z]+")
_PHONE_CHARS = set("0123456789+-() ")


def validate_input(S):
    if not isinstance(S, str):
        return False
    if not (1 <= len(S) <= 40):
        return False
    if _EMAIL.fullmatch(S):
        return True
    if set(S) <= _PHONE_CHARS:
        return 10 <= sum(c.isdigit() for c in S) <= 13
    return False
