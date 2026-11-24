import torch


def batchNormTrain(x, gamma, beta, dy, eps, runningMean, runningVar, momentum):
    """Batch norm in training mode: forward, backward and running-stat update.

    Args:
        x: float32 tensor, shape (batch_size, num_features). Input batch.
        gamma: float32 tensor, shape (num_features,). Scale.
        beta: float32 tensor, shape (num_features,). Shift.
        dy: float32 tensor, shape (batch_size, num_features). Upstream gradient
            dLoss/dy.
        eps: float. Added to the variance for stability.
        runningMean: float32 tensor, shape (num_features,). Running mean before
            this step.
        runningVar: float32 tensor, shape (num_features,). Running variance
            before this step.
        momentum: float. Running-stat update momentum.

    Returns:
        A list [y, dx, dgamma, dbeta, newRunningMean, newRunningVar] (a tuple
        works too):
            y: float32 tensor. Normalized output.
            dx: float32 tensor. Gradient w.r.t. x.
            dgamma: float32 tensor. Gradient w.r.t. gamma.
            dbeta: float32 tensor. Gradient w.r.t. beta.
            newRunningMean: float32 tensor. Updated running mean.
            newRunningVar: float32 tensor. Updated running variance.
    """
    pass
