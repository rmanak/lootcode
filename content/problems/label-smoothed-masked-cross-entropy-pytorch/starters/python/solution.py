import torch


def smoothedMaskedCrossEntropy(logits, targets, mask, smoothing):
    """Masked, label-smoothed cross-entropy and its gradient.

    Args:
        logits: float32 tensor, shape (num_tokens, num_classes). Class scores
            per position.
        targets: int64 tensor, shape (num_tokens,). Correct class per position.
        mask: int64 tensor, shape (num_tokens,). 1 = position counts, 0 =
            ignored.
        smoothing: float. Label-smoothing rate.

    Returns:
        A list [L, grad] (a tuple works too):
            L: 0-dim float32 tensor. Mean loss over unmasked positions.
            grad: float32 tensor. Gradient w.r.t. logits.
    """
    pass
