class StreamStats:
    # Per shard: count, a reference value K (its first value), the mean of (x - K), and M2.
    # Welford on x - K keeps the running mean small, so no digits are lost to a large offset.
    def __init__(self):
        self.n = [0] * 100
        self.ref = [0.0] * 100
        self.mean = [0.0] * 100
        self.m2 = [0.0] * 100

    def add(self, shard, x):
        if self.n[shard] == 0:
            self.ref[shard] = x
        y = x - self.ref[shard]
        self.n[shard] += 1
        delta = y - self.mean[shard]
        self.mean[shard] += delta / self.n[shard]
        self.m2[shard] += delta * (y - self.mean[shard])

    def merge(self, dst, src):
        na, nb = self.n[dst], self.n[src]
        if nb and not na:
            self.n[dst], self.ref[dst] = nb, self.ref[src]
            self.mean[dst], self.m2[dst] = self.mean[src], self.m2[src]
        elif nb:
            n = na + nb
            # Chan et al.; both means are taken relative to dst's reference value.
            delta = (self.ref[src] - self.ref[dst]) + (self.mean[src] - self.mean[dst])
            self.mean[dst] += delta * nb / n
            self.m2[dst] += self.m2[src] + delta * delta * na * nb / n
            self.n[dst] = n
        self.n[src], self.ref[src], self.mean[src], self.m2[src] = 0, 0.0, 0.0, 0.0

    def stats(self, shard):
        n = self.n[shard]
        if n == 0:
            return [0, 0.0, 0.0, 0.0]
        m2 = self.m2[shard]
        return [n, self.ref[shard] + self.mean[shard], m2 / n, m2 / (n - 1) if n > 1 else 0.0]
