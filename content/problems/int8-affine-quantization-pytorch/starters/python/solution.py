import torch


def quantizeInt8(calibration, x):
    """Asymmetric (affine) int8 quantization calibrated on sample data.

    Args:
        calibration: float64 tensor, shape (num_calibration,). Values that set
            the range.
        x: float64 tensor, shape (num_values,). Values to quantize.

    Returns:
        A list [scale, zeroPoint, q, dequantized] (a tuple works too):
            scale: 0-dim float64 tensor. Quantization step.
            zeroPoint: 0-dim int64 tensor. Integer that represents 0.0.
            q: int64 tensor. Quantized x.
            dequantized: float64 tensor. The quantized values mapped back to
                floats.
    """
    pass
