import torch


def quantizeInt8(calibration, x):
    """calibration: (Lc,) and x: (Lx,) float64 tensors.
    Return [scale, zeroPoint, q, dequantized]: scale a 0-dim float64 tensor,
    zeroPoint a 0-dim int64 tensor, q an (Lx,) int64 tensor, dequantized an
    (Lx,) float64 tensor."""
    pass
