import torch


def classifierFreeGuidance(noisePred, guidanceScale, guidanceRescale):
    """Combine conditional and unconditional noise predictions (CFG).

    Args:
        noisePred: float64 tensor, shape (2 * batch_size, latent_dim). The
            batch_size unconditional rows first, then the batch_size
            conditional rows.
        guidanceScale: float. Guidance scale w.
        guidanceRescale: float. Rescale factor in [0, 1].

    Returns:
        A single float64 tensor: the guided noise prediction.
    """
    pass
