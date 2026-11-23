import torch


def quantizeInt8(calibration, x):
    zero = calibration.new_zeros(())
    rmin = torch.minimum(calibration.min(), zero)       # the range always contains 0
    rmax = torch.maximum(calibration.max(), zero)
    scale = (rmax - rmin) / 255
    if scale == 0:
        scale = torch.ones_like(scale)
    # torch.round is round-half-to-even
    zero_point = torch.round(-128 - rmin / scale).clamp(-128, 127).to(torch.int64)
    q = (torch.round(x / scale).to(torch.int64) + zero_point).clamp(-128, 127)
    return [scale, zero_point, q, (q - zero_point).to(x.dtype) * scale]
