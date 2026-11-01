import math


def _source(dst, n_in, n_out, align_corners):
    """Map an output pixel index to a (fractional) input coordinate, like torch.nn.functional.interpolate."""
    if align_corners:
        return dst * (n_in - 1) / (n_out - 1) if n_out > 1 else 0.0
    src = (dst + 0.5) * n_in / n_out - 0.5      # half-pixel centers
    return max(src, 0.0)                        # PyTorch clamps negatives to 0


def _taps(dst, n_in, n_out, align_corners):
    src = _source(dst, n_in, n_out, align_corners)
    i0 = min(int(math.floor(src)), n_in - 1)
    i1 = min(i0 + 1, n_in - 1)
    return i0, i1, src - i0


def resizeBilinear(image, outHeight, outWidth, alignCorners):
    h, w = len(image), len(image[0])
    rows = [_taps(r, h, outHeight, alignCorners) for r in range(outHeight)]
    cols = [_taps(c, w, outWidth, alignCorners) for c in range(outWidth)]
    out = []
    for r0, r1, a in rows:
        top, bottom = image[r0], image[r1]
        line = []
        for c0, c1, b in cols:
            t = top[c0] * (1 - b) + top[c1] * b             # along the row
            u = bottom[c0] * (1 - b) + bottom[c1] * b
            line.append(t * (1 - a) + u * a)                # then between the rows
        out.append(line)
    return out
