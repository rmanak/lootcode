import numpy as np


def trajectoryFeatures(trajectories, speedLimits, dt):
    P = np.asarray(trajectories, float)                        # (B, W, 2)
    seg = np.linalg.norm(np.diff(P, axis=1), axis=2)           # (B, W-1) segment lengths
    speed = seg / dt
    penalty = (np.maximum(0.0, speed - np.asarray(speedLimits, float)) * dt).sum(axis=1)
    remaining = np.zeros(P.shape[:2])
    remaining[:, :-1] = np.cumsum(seg[:, ::-1], axis=1)[:, ::-1]
    return [penalty, remaining]
