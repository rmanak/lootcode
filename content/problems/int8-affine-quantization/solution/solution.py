QMIN, QMAX = -128, 127


def quantizeInt8(calibration, x):
    # The real range always contains 0, so that 0.0 is exactly representable.
    rmin = min(min(calibration), 0.0)
    rmax = max(max(calibration), 0.0)
    scale = (rmax - rmin) / (QMAX - QMIN)
    if scale == 0.0:                    # calibration was all zeros
        scale = 1.0
    # round() on a float is round-half-to-even in Python 3.
    zero_point = min(max(round(QMIN - rmin / scale), QMIN), QMAX)
    q = [min(max(round(v / scale) + zero_point, QMIN), QMAX) for v in x]
    deq = [(k - zero_point) * scale for k in q]
    return [scale, zero_point, q, deq]
