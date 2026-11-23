import torch


def maxPool(x, dout, kernel, stride):
    """2-D max pooling forward and backward pass (per channel).

    Args:
        x: float32 tensor, shape (channels, height, width). Input feature map.
        dout: float32 tensor, shape (channels, out_height, out_width). Upstream
            gradient dLoss/dout.
        kernel: list of ints. [kernel_h, kernel_w].
        stride: int. Step between windows, both axes.

    Returns:
        A list [out, dx] (a tuple works too):
            out: float32 tensor. The pooled output.
            dx: float32 tensor. Gradient w.r.t. x.
    """
    pass
