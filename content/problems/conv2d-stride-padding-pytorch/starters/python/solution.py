import torch


def conv2d(x, weight, bias, stride, padding):
    """2-D convolution of one image, with stride and zero padding.

    Args:
        x: float64 tensor, shape (in_channels, height, width). Input image.
        weight: float64 tensor, shape (out_channels, in_channels, kernel_h,
            kernel_w). Filters.
        bias: float64 tensor, shape (out_channels,). One bias per filter.
        stride: int. Step between windows, both axes.
        padding: int. Zeros added on every side.

    Returns:
        A single float64 tensor: the convolution output.
    """
    pass
