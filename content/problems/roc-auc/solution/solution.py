import numpy as np


def rocAuc(scores, labels):
    s = np.asarray(scores, dtype=float)
    pos = np.asarray(labels) == 1
    n_pos = int(pos.sum())
    n_neg = len(s) - n_pos
    # Rank the scores 1..N from lowest to highest. A run of tied scores shares
    # the average of the ranks it spans, which is what makes a tie count 1/2.
    order = np.argsort(s, kind="stable")
    ss = s[order]
    starts = np.flatnonzero(np.r_[True, ss[1:] != ss[:-1]])   # first index of each run
    ends = np.r_[starts[1:], len(s)]                          # one past its last
    ranks = np.empty(len(s))
    ranks[order] = np.repeat((starts + 1 + ends) / 2.0, ends - starts)
    # Mann-Whitney U: the positives' rank sum minus the least it could be is the
    # number of (positive, negative) pairs the positive wins, ties counting 1/2.
    u = ranks[pos].sum() - n_pos * (n_pos + 1) / 2.0
    return float(u / (n_pos * n_neg))
