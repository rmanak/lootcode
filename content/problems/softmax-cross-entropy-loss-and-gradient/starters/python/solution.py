import numpy as np


def softmaxCrossEntropy(logits, labels):
    """Mean softmax cross-entropy loss and its gradient w.r.t. the logits.

    Args:
        logits: list of lists of floats, shape (batch_size, num_classes). Class
            scores.
        labels: list of ints, shape (batch_size,). Correct class of each row.

    Returns:
        A list [L, grad] (a tuple works too):
            L: float. Mean loss over the batch.
            grad: np.ndarray of floats. Gradient w.r.t. logits.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
