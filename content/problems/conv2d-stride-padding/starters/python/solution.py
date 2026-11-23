import numpy as np


def conv2d(x, weight, bias, stride, padding):
    """2-D convolution of one image, with stride and zero padding.

    Args:
        x: nested list of floats, shape (in_channels, height, width). Input
            image.
        weight: nested list of floats, shape (out_channels, in_channels,
            kernel_h, kernel_w). Filters.
        bias: list of floats, shape (out_channels,). One bias per filter.
        stride: int. Step between windows, both axes.
        padding: int. Zeros added on every side.

    Returns:
        A single np.ndarray of floats: the convolution output.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
