"""Input-constraint validator for problem 'edit-distance'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(word1, word2):
    if not isinstance(word1, str) or not isinstance(word2, str):
        return False
    if len(word1) > 500 or len(word2) > 500:
        return False
    for c in word1:
        if not ('a' <= c <= 'z'):
            return False
    for c in word2:
        if not ('a' <= c <= 'z'):
            return False
    return True
