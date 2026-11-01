import numpy as np


def maxPool(x, dout, kernel, stride):
    x = np.asarray(x, dtype=float)              # (C, H, W)
    dout = np.asarray(dout, dtype=float)        # (C, Hout, Wout)
    kh, kw = kernel
    c, h, w = x.shape
    ho, wo = (h - kh) // stride + 1, (w - kw) // stride + 1
    out = np.empty((c, ho, wo))
    dx = np.zeros_like(x)
    for ch in range(c):
        for r in range(ho):
            for q in range(wo):
                r0, q0 = r * stride, q * stride
                win = x[ch, r0:r0 + kh, q0:q0 + kw]
                k = int(np.argmax(win))         # first maximum in row-major order
                i, j = divmod(k, kw)
                out[ch, r, q] = win[i, j]
                dx[ch, r0 + i, q0 + j] += dout[ch, r, q]    # windows can overlap: accumulate
    return [out.tolist(), dx.tolist()]
