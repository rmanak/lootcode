import numpy as np


def dpoLoss(policyChosen, policyRejected, refChosen, refRejected, beta, labelSmoothing, lossType):
    """Direct Preference Optimization loss, rewards and gradients.

    Args:
        policyChosen: list of floats, shape (batch_size,). Policy log-probs of
            the chosen responses.
        policyRejected: list of floats, shape (batch_size,). Policy log-probs
            of the rejected responses.
        refChosen: list of floats, shape (batch_size,). Reference log-probs of
            the chosen responses.
        refRejected: list of floats, shape (batch_size,). Reference log-probs
            of the rejected responses.
        beta: float. KL-penalty strength.
        labelSmoothing: float. Label-smoothing rate (0 for ipo).
        lossType: str. "sigmoid" or "ipo".

    Returns:
        A list [loss, chosenRewards, rejectedRewards, rewardAccuracy,
        gradChosen, gradRejected] (a tuple works too):
            loss: float. Mean loss over the batch.
            chosenRewards: np.ndarray of floats. Implicit rewards of the chosen
                responses.
            rejectedRewards: np.ndarray of floats. Implicit rewards of the
                rejected responses.
            rewardAccuracy: float. Fraction of pairs ranked correctly.
            gradChosen: np.ndarray of floats. Gradient of loss w.r.t.
                policyChosen.
            gradRejected: np.ndarray of floats. Gradient of loss w.r.t.
                policyRejected.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
