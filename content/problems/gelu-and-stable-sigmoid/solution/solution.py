import math


def activations(x):
    sig, dsig, logsig, gelu, dgelu = [], [], [], [], []
    for v in x:
        # Never exponentiate a large positive number: pick the form whose exp is <= 1.
        if v >= 0:
            e = math.exp(-v)
            s = 1.0 / (1.0 + e)
            ls = -math.log1p(e)                 # log sigmoid(v) = -log(1 + e^-v)
        else:
            e = math.exp(v)
            s = e / (1.0 + e)
            ls = v - math.log1p(e)              # = v - log(1 + e^v)
        sig.append(s)
        dsig.append(s * (1.0 - s))
        logsig.append(ls)
        cdf = 0.5 * (1.0 + math.erf(v / math.sqrt(2.0)))     # standard normal CDF
        pdf = math.exp(-0.5 * v * v) / math.sqrt(2.0 * math.pi)
        gelu.append(v * cdf)
        dgelu.append(cdf + v * pdf)
    return [sig, dsig, logsig, gelu, dgelu]
