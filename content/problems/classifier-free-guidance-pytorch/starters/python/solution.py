import torch


def classifierFreeGuidance(noisePred, guidanceScale, guidanceRescale):
    """noisePred: (2B, N) float64 tensor (unconditional rows first);
    guidanceScale, guidanceRescale: float.
    Return the (B, N) float64 guided prediction."""
    pass
