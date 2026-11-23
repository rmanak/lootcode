import numpy as np


def maxPool(x, dout, kernel, stride):
    """2-D max pooling forward and backward pass (per channel).

    Args:
        x: nested list of floats, shape (channels, height, width). Input
            feature map.
        dout: nested list of floats, shape (channels, out_height, out_width).
            Upstream gradient dLoss/dout.
        kernel: list of ints. [kernel_h, kernel_w].
        stride: int. Step between windows, both axes.

    Returns:
        A list [out, dx] (a tuple works too):
            out: np.ndarray of floats. The pooled output.
            dx: np.ndarray of floats. Gradient w.r.t. x.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
