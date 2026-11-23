import torch


def resizeBilinear(image, outHeight, outWidth, alignCorners):
    """Resize a single-channel image with bilinear interpolation.

    Args:
        image: float64 tensor, shape (height, width). Pixel values.
        outHeight: int. Target height.
        outWidth: int. Target width.
        alignCorners: bool. The align_corners convention.

    Returns:
        A single float64 tensor: the resized image.
    """
    pass
