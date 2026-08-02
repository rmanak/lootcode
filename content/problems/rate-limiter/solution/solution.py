from collections import defaultdict, deque


class RateLimiter:
    def __init__(self, limit, window):
        self.limit = limit
        self.window = window
        self.hist = defaultdict(deque)

    def request(self, userId, timestamp):
        dq = self.hist[userId]
        while dq and dq[0] <= timestamp - self.window:
            dq.popleft()
        if len(dq) < self.limit:
            dq.append(timestamp)
            return True
        return False
