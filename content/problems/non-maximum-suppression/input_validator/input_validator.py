"""Input-constraint validator for problem 'non-maximum-suppression'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: 1 <= N <= 1000 boxes, each a list of 4 finite
numbers [x1, y1, x2, y2] with |coordinate| <= 10^4 and x1 < x2, y1 < y2 (the
promise that every box has positive area, so a union is never 0); exactly N
scores, each finite with |score| <= 10^6; and 0 <= iouThreshold <= 1.
"""
import math

MAX_N, MAX_COORD, MAX_SCORE = 1000, 10_000, 1_000_000


def _num(v, bound):
    return (isinstance(v, (int, float)) and not isinstance(v, bool)
            and math.isfinite(v) and abs(v) <= bound)


def validate_input(boxes, scores, iouThreshold):
    if not isinstance(boxes, list) or not 1 <= len(boxes) <= MAX_N:
        return False
    for box in boxes:
        if not isinstance(box, list) or len(box) != 4:
            return False
        if not all(_num(v, MAX_COORD) for v in box):
            return False
        if not (box[0] < box[2] and box[1] < box[3]):
            return False
    if not isinstance(scores, list) or len(scores) != len(boxes):
        return False
    if not all(_num(s, MAX_SCORE) for s in scores):
        return False
    return _num(iouThreshold, 1) and 0 <= iouThreshold <= 1
