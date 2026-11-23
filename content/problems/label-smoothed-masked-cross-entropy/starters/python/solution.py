import numpy as np


def smoothedMaskedCrossEntropy(logits, targets, mask, smoothing):
    """Masked, label-smoothed cross-entropy and its gradient.

    Args:
        logits: list of lists of floats, shape (num_tokens, num_classes). Class
            scores per position.
        targets: list of ints, shape (num_tokens,). Correct class per position.
        mask: list of ints, shape (num_tokens,). 1 = position counts, 0 =
            ignored.
        smoothing: float. Label-smoothing rate.

    Returns:
        A list [L, grad] (a tuple works too):
            L: float. Mean loss over unmasked positions.
            grad: np.ndarray of floats. Gradient w.r.t. logits.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
