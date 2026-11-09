"""Input-constraint validator for problem 'longest-match-tokenizer'.

Hand-written. text is a str of 0..1e5 printable ASCII characters; vocab a
dict of 1..1e4 entries, keys non-empty printable-ASCII strs of length <= 20,
values ints in [-1e9, 1e9]; unkId an int in that range; mergeUnk a bool.
"""


def _ascii(s):
    return all(32 <= ord(c) < 127 for c in s)


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool) and -10**9 <= v <= 10**9


def validate_input(text, vocab, unkId, mergeUnk):
    if not isinstance(text, str) or len(text) > 10**5 or not _ascii(text):
        return False
    if not isinstance(vocab, dict) or not 1 <= len(vocab) <= 10**4:
        return False
    for k, v in vocab.items():
        if not isinstance(k, str) or not 1 <= len(k) <= 20 or not _ascii(k) or not _int(v):
            return False
    return _int(unkId) and isinstance(mergeUnk, bool)
