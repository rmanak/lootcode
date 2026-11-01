"""Input-constraint validator for problem 'tf-idf-cosine-retrieval'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: documents a list of 1..200 strings of at most 1000
printable ASCII characters; queries a list of 1..20 such strings of at most
200 characters; k an int with 1 <= k <= len(documents).

Not checked here: the promise that within each query's top k + 1 documents,
two scores are either exactly equal (duplicate token counts, or both 0) or
differ by more than a relative 1e-9. The case generator vets that.
"""


def _text(s, limit):
    return isinstance(s, str) and len(s) <= limit and all(32 <= ord(ch) <= 126 for ch in s)


def validate_input(documents, queries, k):
    if not isinstance(documents, list) or not 1 <= len(documents) <= 200:
        return False
    if not all(_text(d, 1000) for d in documents):
        return False
    if not isinstance(queries, list) or not 1 <= len(queries) <= 20:
        return False
    if not all(_text(q, 200) for q in queries):
        return False
    return isinstance(k, int) and not isinstance(k, bool) and 1 <= k <= len(documents)
