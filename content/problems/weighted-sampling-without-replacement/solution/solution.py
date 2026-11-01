import math


def weightedSample(weights, k, u):
    # Efraimidis-Spirakis: item i gets the key u_i ** (1 / w_i); keep the k largest.
    # Compare log(key) = log(u_i) / w_i instead: u ** (1 / w) underflows to 0
    # for small weights, and every such item would then tie at 0.
    log_key = [math.log(ui) / wi for ui, wi in zip(u, weights)]
    order = sorted(range(len(weights)), key=lambda i: (-log_key[i], i))
    return order[:k]
