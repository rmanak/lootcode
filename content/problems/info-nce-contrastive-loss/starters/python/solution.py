import numpy as np


def infoNCE(U, V, temperature):
    """Symmetric InfoNCE (CLIP-style) loss and its gradients.

    Args:
        U: list of lists of floats, shape (batch_size, embed_dim). Image
            embeddings.
        V: list of lists of floats, shape (batch_size, embed_dim). Text
            embeddings; row i matches row i of U.
        temperature: float. Softmax temperature.

    Returns:
        A list [loss, dU, dV] (a tuple works too):
            loss: float. The symmetric loss.
            dU: np.ndarray of floats. Gradient w.r.t. U.
            dV: np.ndarray of floats. Gradient w.r.t. V.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
