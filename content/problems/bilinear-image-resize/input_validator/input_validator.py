"""Input-constraint validator for problem 'bilinear-image-resize'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: image is H x W with 1 <= H, W <= 64, every pixel
finite (not a bool) in [0, 255]; outHeight and outWidth ints in [1, 64];
alignCorners a bool.
"""
import math


def _px(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and 0 <= v <= 255


def validate_input(image, outHeight, outWidth, alignCorners):
    if not isinstance(image, list) or not 1 <= len(image) <= 64 or not isinstance(image[0], list):
        return False
    w = len(image[0])
    if not 1 <= w <= 64:
        return False
    if not all(isinstance(r, list) and len(r) == w and all(_px(v) for v in r) for r in image):
        return False
    for n in (outHeight, outWidth):
        if not (isinstance(n, int) and not isinstance(n, bool) and 1 <= n <= 64):
            return False
    return isinstance(alignCorners, bool)
