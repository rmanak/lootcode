import torch


def resizeBilinear(image, outHeight, outWidth, alignCorners):
    """Resize a single-channel image with bilinear interpolation.

    Args:
        image: float32 tensor, shape (height, width). Pixel values.
        outHeight: int. Target height.
        outWidth: int. Target width.
        alignCorners: bool. The align_corners convention.

    Returns:
        A single float32 tensor: the resized image.
    """
    pass
