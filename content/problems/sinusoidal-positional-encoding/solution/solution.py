import numpy as np


def positionalEncoding(positions, d, base):
    pos = np.asarray(positions, dtype=float)[:, None]       # (n, 1)
    cols = np.arange(d)
    pair = cols // 2                                        # columns 2i and 2i+1 share frequency i
    angle = pos / base ** (2.0 * pair / d)                  # (n, d)
    pe = np.where(cols % 2 == 0, np.sin(angle), np.cos(angle))   # even column: sin, odd: cos
    return pe.tolist()
