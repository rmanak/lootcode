import numpy as np


def classifierFreeGuidance(noisePred, guidanceScale, guidanceRescale):
    pred = np.asarray(noisePred, dtype=float)   # (2B, N): unconditional rows first, then conditional
    b = pred.shape[0] // 2
    uncond, cond = pred[:b], pred[b:]
    guided = uncond + guidanceScale * (cond - uncond)
    if guidanceRescale > 0:
        # Match each sample's std to the conditional prediction's std, then blend.
        std_cond = cond.std(axis=1, ddof=1, keepdims=True)
        std_guided = guided.std(axis=1, ddof=1, keepdims=True)
        rescaled = guided * (std_cond / std_guided)
        guided = guidanceRescale * rescaled + (1 - guidanceRescale) * guided
    return guided.tolist()
