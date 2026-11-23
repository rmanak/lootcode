import torch


def dpoLoss(policyChosen, policyRejected, refChosen, refRejected, beta, labelSmoothing, lossType):
    """policyChosen, policyRejected, refChosen, refRejected: (B,) float64 tensors;
    beta, labelSmoothing: float; lossType: "sigmoid" or "ipo".
    Return [loss, chosenRewards, rejectedRewards, rewardAccuracy, gradChosen,
    gradRejected]: loss and rewardAccuracy 0-dim float64 tensors, the rest (B,)."""
    pass
