import numpy as np


class Adam:
    def __init__(self, params, lr, beta1, beta2, eps):
        self.theta = np.asarray(params, dtype=float).copy()
        self.lr, self.beta1, self.beta2, self.eps = lr, beta1, beta2, eps
        self.m = np.zeros_like(self.theta)   # first moment (mean of gradients)
        self.v = np.zeros_like(self.theta)   # second moment (mean of squared gradients)
        self.t = 0

    def step(self, grad):
        g = np.asarray(grad, dtype=float)
        self.t += 1
        self.m = self.beta1 * self.m + (1 - self.beta1) * g
        self.v = self.beta2 * self.v + (1 - self.beta2) * g * g
        # Both moments start at 0, so early on they are biased toward 0;
        # dividing by 1 - beta^t undoes that.
        m_hat = self.m / (1 - self.beta1 ** self.t)
        v_hat = self.v / (1 - self.beta2 ** self.t)
        self.theta = self.theta - self.lr * m_hat / (np.sqrt(v_hat) + self.eps)
        return self.theta.tolist()
