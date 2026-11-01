"""Input-constraint validator for problem 'bpe-tokenizer'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: corpus is a list of 1..300 words, each a string of
1..20 lowercase ASCII letters a-z; numMerges is an int with
0 <= numMerges <= 200; word is a string of 1..30 lowercase letters a-z. Every
tie is pinned by the statement, so there is no promise about the answer.
"""

LETTERS = set("abcdefghijklmnopqrstuvwxyz")


def _word(s, max_len):
    return isinstance(s, str) and 1 <= len(s) <= max_len and set(s) <= LETTERS


def validate_input(corpus, numMerges, word):
    if not isinstance(corpus, list) or not 1 <= len(corpus) <= 300:
        return False
    if not all(_word(w, 20) for w in corpus):
        return False
    if not (isinstance(numMerges, int) and not isinstance(numMerges, bool)
            and 0 <= numMerges <= 200):
        return False
    return _word(word, 30)
