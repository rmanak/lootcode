import math


class StreamingEntropy:
    def __init__(self):
        self.m = None      # running max
        self.s = 0.0       # sum of exp(x - m)
        self.u = 0.0       # sum of exp(x - m) * (x - m)

    def update(self, chunk):
        if not chunk:
            return
        new_m = max(chunk) if self.m is None else max(self.m, max(chunk))
        if self.m is not None and new_m > self.m:
            delta = self.m - new_m                 # < 0
            scale = math.exp(delta)
            # each old term e^(x-m)(x-m) becomes e^(x-m')(x-m') = scale * e^(x-m) * ((x-m) + delta)
            self.u = scale * (self.u + delta * self.s)
            self.s = scale * self.s
        self.m = new_m
        for x in chunk:
            d = x - new_m
            w = math.exp(d)
            self.s += w
            self.u += w * d

    def entropy(self):
        return math.log(self.s) - self.u / self.s
