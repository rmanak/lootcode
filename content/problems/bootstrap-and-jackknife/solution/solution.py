import numpy as np


def _leave_one_out_means(x):
    m = x.mean()
    return m - (x - m) / (len(x) - 1)        # mean of x without each element in turn


def abUncertainty(groups, values, resample0, resample1, alpha):
    g = np.asarray(groups)
    v = np.asarray(values, float)
    v = v - v.mean()                         # shift-invariant; exact for values near the mean
    x0, x1 = v[g == 0], v[g == 1]
    m0, m1 = x0.mean(), x1.mean()
    estimate = m1 - m0

    boot = x1[np.asarray(resample1)].mean(axis=1) - x0[np.asarray(resample0)].mean(axis=1)
    lo, hi = np.percentile(boot, [100 * alpha / 2, 100 * (1 - alpha / 2)])

    jack = np.concatenate([m1 - _leave_one_out_means(x0), _leave_one_out_means(x1) - m0])
    n = len(v)
    se = np.sqrt((n - 1) / n * np.sum((jack - jack.mean()) ** 2))
    return [float(estimate), float(lo), float(hi), float(se)]
