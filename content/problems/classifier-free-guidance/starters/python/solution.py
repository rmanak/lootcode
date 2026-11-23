import numpy as np


def classifierFreeGuidance(noisePred, guidanceScale, guidanceRescale):
    """Combine conditional and unconditional noise predictions (CFG).

    Args:
        noisePred: list of lists of floats, shape (2 * batch_size, latent_dim).
            The batch_size unconditional rows first, then the batch_size
            conditional rows.
        guidanceScale: float. Guidance scale w.
        guidanceRescale: float. Rescale factor in [0, 1].

    Returns:
        A single np.ndarray of floats: the guided noise prediction.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
