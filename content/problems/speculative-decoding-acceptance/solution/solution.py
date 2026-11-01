def _sample(weights, u):
    """Inverse CDF on unnormalized weights: the smallest j with cumsum[j] > u * total."""
    target = u * sum(weights)
    acc = 0.0
    for j, w in enumerate(weights):
        acc += w
        if acc > target:
            return j
    return max(j for j, w in enumerate(weights) if w > 0)    # rounding fallback: last token with mass


def speculativeStep(draftTokens, draftProbs, targetProbs, u, uSample):
    out = []
    for i, x in enumerate(draftTokens):
        p, q = targetProbs[i][x], draftProbs[i][x]
        if u[i] < p / q:                                    # accept with probability min(1, p/q)
            out.append(x)
            continue
        # Rejected: resample from the residual max(0, p - q), which makes the
        # overall output distributed exactly as the target model.
        residual = [max(0.0, a - b) for a, b in zip(targetProbs[i], draftProbs[i])]
        out.append(_sample(residual, uSample))
        return [out, i]
    out.append(_sample(targetProbs[len(draftTokens)], uSample))   # all accepted: a free bonus token
    return [out, len(draftTokens)]
