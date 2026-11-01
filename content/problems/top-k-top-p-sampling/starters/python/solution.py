import numpy as np


def sampleToken(logits, temperature, topK, topP, u):
    """logits: V numbers. temperature > 0. 1 <= topK <= V. 0 < topP <= 1. 0 <= u < 1.
    Return [token, probs]: the sampled token id and the final V-entry distribution."""
    pass
