import torch


def loraForward(X, W, A, B, alpha, useRsLora):
    """LoRA adapter forward pass, and the merged weight matrix.

    Args:
        X: float32 tensor, shape (batch_size, in_features). Layer input.
        W: float32 tensor, shape (in_features, out_features). Frozen base
            weights.
        A: float32 tensor, shape (in_features, rank). LoRA down-projection.
        B: float32 tensor, shape (rank, out_features). LoRA up-projection.
        alpha: float. LoRA scaling numerator.
        useRsLora: bool. Use rank-stabilized scaling.

    Returns:
        A list [Y, mergedW] (a tuple works too):
            Y: float32 tensor. The adapted layer's output.
            mergedW: float32 tensor. Base weights with the adapter folded in.
    """
    pass
