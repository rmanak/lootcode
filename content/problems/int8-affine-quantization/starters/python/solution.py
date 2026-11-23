def quantizeInt8(calibration, x):
    """Asymmetric (affine) int8 quantization calibrated on sample data.

    Args:
        calibration: list of floats, shape (num_calibration,). Values that set
            the range.
        x: list of floats, shape (num_values,). Values to quantize.

    Returns:
        A list [scale, zeroPoint, q, dequantized] (a tuple works too):
            scale: float. Quantization step.
            zeroPoint: int. Integer that represents 0.0.
            q: np.ndarray of ints. Quantized x.
            dequantized: np.ndarray of floats. The quantized values mapped back
                to floats.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
