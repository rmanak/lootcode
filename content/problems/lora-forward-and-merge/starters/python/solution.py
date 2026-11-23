import math

import numpy as np


def loraForward(X, W, A, B, alpha, useRsLora):
    """LoRA adapter forward pass, and the merged weight matrix.

    Args:
        X: list of lists of floats, shape (batch_size, in_features). Layer
            input.
        W: list of lists of floats, shape (in_features, out_features). Frozen
            base weights.
        A: list of lists of floats, shape (in_features, rank). LoRA
            down-projection.
        B: list of lists of floats, shape (rank, out_features). LoRA
            up-projection.
        alpha: float. LoRA scaling numerator.
        useRsLora: bool. Use rank-stabilized scaling.

    Returns:
        A list [Y, mergedW] (a tuple works too):
            Y: np.ndarray of floats. The adapted layer's output.
            mergedW: np.ndarray of floats. Base weights with the adapter folded
                in.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
