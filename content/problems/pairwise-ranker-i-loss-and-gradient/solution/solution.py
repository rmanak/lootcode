import numpy as np


def rankingLossAndGrad(preferences, w):
    pairs = np.asarray(preferences, dtype=float)    # (N, 2, d)
    diff = pairs[:, 0, :] - pairs[:, 1, :]          # x1 - x2, one row per pair
    margins = diff @ np.asarray(w, dtype=float)
    # log(1 + e^-m) without ever exponentiating a large positive number
    loss = np.logaddexp(0.0, -margins).mean()
    # how hard each pair pulls on w: sigmoid(-m), written so it cannot overflow
    pull = 0.5 * (1.0 - np.tanh(0.5 * margins))
    grad = -(pull @ diff) / len(diff)
    return float(loss), grad.tolist()
