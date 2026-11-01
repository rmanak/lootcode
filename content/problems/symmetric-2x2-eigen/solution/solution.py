import math


def _eigen(a, b, c):
    if b == 0:                                    # already diagonal (a multiple of I when a == c)
        if a >= c:
            return [a, c, [1.0, 0.0], [0.0, 1.0]]
        return [c, a, [0.0, 1.0], [-1.0, 0.0]]
    m = (a + c) / 2
    h = (a - c) / 2
    r = math.hypot(h, b)                          # half the gap between the eigenvalues
    big = m + math.copysign(r, m)                 # the larger-magnitude eigenvalue: no cancellation
    small = (a * c - b * b) / big                 # the other one, from det = lambda1 * lambda2
    lam1, lam2 = max(big, small), min(big, small)
    theta = 0.5 * math.atan2(b, h)                # tan(2 theta) = 2b / (a - c); theta in (-pi/2, pi/2)
    v1 = [math.cos(theta), math.sin(theta)]       # cos(theta) > 0: the required sign
    return [lam1, lam2, v1, [-v1[1], v1[0]]]


def symmetricEigen2x2(matrices):
    return [_eigen(M[0][0], M[0][1], M[1][1]) for M in matrices]
