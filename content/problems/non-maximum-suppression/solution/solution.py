import numpy as np


def nonMaxSuppression(boxes, scores, iouThreshold):
    b = np.asarray(boxes, dtype=float).reshape(-1, 4)
    n = len(b)
    # Highest score first; equal scores keep their input order (lower index first).
    order = sorted(range(n), key=lambda i: (-scores[i], i))
    area = (b[:, 2] - b[:, 0]) * (b[:, 3] - b[:, 1])
    removed = np.zeros(n, dtype=bool)
    keep = []
    for i in order:
        if removed[i]:
            continue
        keep.append(i)
        # Overlap of box i with every box; a negative width or height means
        # no overlap along that axis, so clamp each at 0 before multiplying.
        w = np.clip(np.minimum(b[i, 2], b[:, 2]) - np.maximum(b[i, 0], b[:, 0]), 0, None)
        h = np.clip(np.minimum(b[i, 3], b[:, 3]) - np.maximum(b[i, 1], b[:, 1]), 0, None)
        inter = w * h
        iou = inter / (area[i] + area - inter)
        removed |= iou > iouThreshold      # strictly greater: equal IoU survives
    return keep
