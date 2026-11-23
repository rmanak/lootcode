import torch


def infoNCE(U, V, temperature):
    """Symmetric InfoNCE (CLIP-style) loss and its gradients.

    Args:
        U: float64 tensor, shape (batch_size, embed_dim). Image embeddings.
        V: float64 tensor, shape (batch_size, embed_dim). Text embeddings; row
            i matches row i of U.
        temperature: float. Softmax temperature.

    Returns:
        A list [loss, dU, dV] (a tuple works too):
            loss: 0-dim float64 tensor. The symmetric loss.
            dU: float64 tensor. Gradient w.r.t. U.
            dV: float64 tensor. Gradient w.r.t. V.
    """
    pass
