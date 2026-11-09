from collections import deque

import numpy as np


class StorageForecaster:
    def __init__(self, windowSize):
        self.samples = deque(maxlen=windowSize)

    def recordUsage(self, timestamp, usedBytes):
        self.samples.append((timestamp, usedBytes))

    def _fit(self):
        """Return (slope, mean_t, mean_y), or None with fewer than 2 samples."""
        if len(self.samples) < 2:
            return None
        t = np.array([s[0] for s in self.samples], float)
        y = np.array([s[1] for s in self.samples], float)
        mt, my = t.mean(), y.mean()
        tc, yc = t - mt, y - my
        return (tc @ yc) / (tc @ tc), mt, my

    def forecastFull(self, totalBytes):
        fit = self._fit()
        if fit is None or fit[0] <= 0:
            return -1
        b, mt, my = fit
        return float(mt + (totalBytes - my) / b)

    def getGrowthRatePerDay(self):
        fit = self._fit()
        return 0.0 if fit is None else float(fit[0] * 86400)
