class WeightedPicker:
    def __init__(self, weights):
        self.n = len(weights)
        self.w = list(weights)
        self.tree = [0] * (self.n + 1)          # Fenwick tree over 1-based positions
        for i, x in enumerate(weights, 1):      # O(n) build
            self.tree[i] += x
            j = i + (i & -i)
            if j <= self.n:
                self.tree[j] += self.tree[i]
        self.sum = sum(weights)
        self.top = 1 << self.n.bit_length()

    def update(self, i, weight):
        delta = weight - self.w[i]
        self.w[i] = weight
        self.sum += delta
        k = i + 1
        while k <= self.n:
            self.tree[k] += delta
            k += k & -k

    def pick(self, r):
        # Largest position p with prefix(p) <= r; the answer is item p (0-based).
        pos, step = 0, self.top
        while step:
            nxt = pos + step
            if nxt <= self.n and self.tree[nxt] <= r:
                pos = nxt
                r -= self.tree[nxt]
            step >>= 1
        return pos

    def total(self):
        return self.sum
