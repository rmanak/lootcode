"""Input-constraint validator for problem 'pruneGraph' ('prune-computation-graph').

Hand-written. nodes: 1..5000 entries [name, op, inputs] with name and op
non-empty strs of <= 20 chars and inputs a list of <= 8 strs of <= 20 chars
(whether they name real nodes is part of the problem); output a str of
<= 20 chars.
"""


def _s(v, allow_empty=False):
    return isinstance(v, str) and (allow_empty or len(v) >= 1) and len(v) <= 20


def validate_input(nodes, output):
    if not isinstance(nodes, list) or not 1 <= len(nodes) <= 5000:
        return False
    for nd in nodes:
        if not isinstance(nd, list) or len(nd) != 3:
            return False
        name, op, inputs = nd
        if not _s(name) or not _s(op) or not isinstance(inputs, list) or len(inputs) > 8:
            return False
        if not all(_s(x) for x in inputs):
            return False
    return _s(output)
