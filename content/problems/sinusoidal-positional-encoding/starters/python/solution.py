import numpy as np


def positionalEncoding(positions, d, base):
    """Sinusoidal positional encodings for a list of positions.

    Args:
        positions: list of ints, shape (num_positions,). The positions to
            encode.
        d: int. Encoding width.
        base: float. Frequency base.

    Returns:
        A single np.ndarray of floats: one encoding per position.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
