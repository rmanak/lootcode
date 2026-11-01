import numpy as np


def applyRope(x, positions, base, style):
    x = np.asarray(x, dtype=float)                          # (T, d)
    d = x.shape[1]
    half = d // 2
    theta = base ** (-2.0 * np.arange(half) / d)            # one frequency per pair
    ang = np.asarray(positions, dtype=float)[:, None] * theta[None, :]   # (T, d/2)
    cos, sin = np.cos(ang), np.sin(ang)
    if style == "interleaved":
        a, b = x[:, 0::2], x[:, 1::2]                       # pairs (0,1), (2,3), ...
    else:                                                   # "half": pairs (i, i + d/2)
        a, b = x[:, :half], x[:, half:]
    ra = a * cos - b * sin
    rb = a * sin + b * cos
    out = np.empty_like(x)
    if style == "interleaved":
        out[:, 0::2], out[:, 1::2] = ra, rb
    else:
        out[:, :half], out[:, half:] = ra, rb
    return out.tolist()
