import torch


def dpoLoss(policyChosen, policyRejected, refChosen, refRejected, beta, labelSmoothing, lossType):
    """Direct Preference Optimization loss, rewards and gradients.

    Args:
        policyChosen: float64 tensor, shape (batch_size,). Policy log-probs of
            the chosen responses.
        policyRejected: float64 tensor, shape (batch_size,). Policy log-probs
            of the rejected responses.
        refChosen: float64 tensor, shape (batch_size,). Reference log-probs of
            the chosen responses.
        refRejected: float64 tensor, shape (batch_size,). Reference log-probs
            of the rejected responses.
        beta: float. KL-penalty strength.
        labelSmoothing: float. Label-smoothing rate (0 for ipo).
        lossType: str. "sigmoid" or "ipo".

    Returns:
        A list [loss, chosenRewards, rejectedRewards, rewardAccuracy,
        gradChosen, gradRejected] (a tuple works too):
            loss: 0-dim float64 tensor. Mean loss over the batch.
            chosenRewards: float64 tensor. Implicit rewards of the chosen
                responses.
            rejectedRewards: float64 tensor. Implicit rewards of the rejected
                responses.
            rewardAccuracy: 0-dim float64 tensor. Fraction of pairs ranked
                correctly.
            gradChosen: float64 tensor. Gradient of loss w.r.t. policyChosen.
            gradRejected: float64 tensor. Gradient of loss w.r.t.
                policyRejected.
    """
    pass
