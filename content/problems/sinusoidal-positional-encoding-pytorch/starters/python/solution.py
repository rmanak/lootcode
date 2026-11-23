import torch


def positionalEncoding(positions, d, base):
    """Sinusoidal positional encodings for a list of positions.

    Args:
        positions: int64 tensor, shape (num_positions,). The positions to
            encode.
        d: int. Encoding width.
        base: float. Frequency base.

    Returns:
        A single float64 tensor: one encoding per position.
    """
    pass
