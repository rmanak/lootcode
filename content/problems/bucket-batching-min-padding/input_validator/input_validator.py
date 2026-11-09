"""Input-constraint validator for problem 'bucket-batching-min-padding'.

Hand-written. lengths: 1..200 ints (not bools) in [1, 1e6]; G an int with
1 <= G <= len(lengths).
"""


def validate_input(lengths, G):
    if not isinstance(lengths, list) or not 1 <= len(lengths) <= 200:
        return False
    if not all(isinstance(x, int) and not isinstance(x, bool) and 1 <= x <= 10**6 for x in lengths):
        return False
    return isinstance(G, int) and not isinstance(G, bool) and 1 <= G <= len(lengths)
