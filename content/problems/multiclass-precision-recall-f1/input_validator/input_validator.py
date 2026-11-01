"""Input-constraint validator for problem 'multiclass-precision-recall-f1'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: numClasses an int with 2 <= numClasses <= 20;
yTrue and yPred lists of the same length N with 1 <= N <= 10^4, every entry an
int in [0, numClasses).
"""


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def validate_input(yTrue, yPred, numClasses):
    if not (_int(numClasses) and 2 <= numClasses <= 20):
        return False
    if not (isinstance(yTrue, list) and isinstance(yPred, list) and 1 <= len(yTrue) <= 10_000
            and len(yPred) == len(yTrue)):
        return False
    return all(_int(v) and 0 <= v < numClasses for v in yTrue + yPred)
