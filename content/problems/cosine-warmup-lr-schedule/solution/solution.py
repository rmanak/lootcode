import math


def learningRates(steps, baseLr, minLr, warmupSteps, totalSteps):
    out = []
    for t in steps:
        if t < warmupSteps:
            out.append(baseLr * t / warmupSteps)                    # linear warmup from 0
        elif t >= totalSteps:
            out.append(float(minLr))                                # stays at the floor
        else:
            progress = (t - warmupSteps) / (totalSteps - warmupSteps)
            out.append(minLr + (baseLr - minLr) * 0.5 * (1.0 + math.cos(math.pi * progress)))
    return out
