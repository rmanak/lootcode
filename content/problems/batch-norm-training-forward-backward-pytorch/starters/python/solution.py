import torch


def batchNormTrain(x, gamma, beta, dy, eps, runningMean, runningVar, momentum):
    """Batch norm in training mode: forward, backward and running-stat update.

    Args:
        x: float64 tensor, shape (batch_size, num_features). Input batch.
        gamma: float64 tensor, shape (num_features,). Scale.
        beta: float64 tensor, shape (num_features,). Shift.
        dy: float64 tensor, shape (batch_size, num_features). Upstream gradient
            dLoss/dy.
        eps: float. Added to the variance for stability.
        runningMean: float64 tensor, shape (num_features,). Running mean before
            this step.
        runningVar: float64 tensor, shape (num_features,). Running variance
            before this step.
        momentum: float. Running-stat update momentum.

    Returns:
        A list [y, dx, dgamma, dbeta, newRunningMean, newRunningVar] (a tuple
        works too):
            y: float64 tensor. Normalized output.
            dx: float64 tensor. Gradient w.r.t. x.
            dgamma: float64 tensor. Gradient w.r.t. gamma.
            dbeta: float64 tensor. Gradient w.r.t. beta.
            newRunningMean: float64 tensor. Updated running mean.
            newRunningVar: float64 tensor. Updated running variance.
    """
    pass
