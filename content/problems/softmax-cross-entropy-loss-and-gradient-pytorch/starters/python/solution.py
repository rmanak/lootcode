import torch


def softmaxCrossEntropy(logits, labels):
    """Mean softmax cross-entropy loss and its gradient w.r.t. the logits.

    Args:
        logits: float32 tensor, shape (batch_size, num_classes). Class scores.
        labels: int64 tensor, shape (batch_size,). Correct class of each row.

    Returns:
        A list [L, grad] (a tuple works too):
            L: 0-dim float32 tensor. Mean loss over the batch.
            grad: float32 tensor. Gradient w.r.t. logits.
    """
    pass
