import numpy as np


def dpoLoss(policyChosen, policyRejected, refChosen, refRejected, beta, labelSmoothing, lossType):
    pc, pr = np.asarray(policyChosen, dtype=float), np.asarray(policyRejected, dtype=float)
    rc, rr = np.asarray(refChosen, dtype=float), np.asarray(refRejected, dtype=float)
    n = len(pc)
    h = (pc - pr) - (rc - rr)                   # how much more the policy prefers chosen than the reference does
    if lossType == "sigmoid":
        z = beta * h
        eps = labelSmoothing
        # -log sigmoid(z) = logaddexp(0, -z): never exp() of a large positive number.
        losses = (1 - eps) * np.logaddexp(0.0, -z) + eps * np.logaddexp(0.0, z)
        sig_neg = 0.5 * (1.0 - np.tanh(0.5 * z))  # sigmoid(-z)
        dh = beta * (-(1 - eps) * sig_neg + eps * (1.0 - sig_neg))
    else:                                       # "ipo"
        target = 1.0 / (2.0 * beta)
        losses = (h - target) ** 2
        dh = 2.0 * (h - target)
    chosen_rewards = beta * (pc - rc)
    rejected_rewards = beta * (pr - rr)
    accuracy = float(np.mean(chosen_rewards > rejected_rewards))
    grad_chosen = dh / n                        # d(mean loss) / d policyChosen[i]
    return [float(losses.mean()), chosen_rewards.tolist(), rejected_rewards.tolist(), accuracy,
            grad_chosen.tolist(), (-grad_chosen).tolist()]
