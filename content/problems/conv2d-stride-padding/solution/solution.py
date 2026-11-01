import numpy as np


def conv2d(x, weight, bias, stride, padding):
    x = np.asarray(x, dtype=float)              # (Cin, H, W)
    w = np.asarray(weight, dtype=float)         # (Cout, Cin, kH, kW)
    cout, cin, kh, kw = w.shape
    xp = np.pad(x, ((0, 0), (padding, padding), (padding, padding)))   # zeros on every side
    ho = (xp.shape[1] - kh) // stride + 1
    wo = (xp.shape[2] - kw) // stride + 1
    out = np.zeros((cout, ho, wo))
    # Cross-correlation (no kernel flip): accumulate one kernel offset at a time.
    for i in range(kh):
        for j in range(kw):
            patch = xp[:, i:i + stride * (ho - 1) + 1:stride, j:j + stride * (wo - 1) + 1:stride]
            out += np.einsum("oc,chw->ohw", w[:, :, i, j], patch)
    out += np.asarray(bias, dtype=float)[:, None, None]
    return out.tolist()
