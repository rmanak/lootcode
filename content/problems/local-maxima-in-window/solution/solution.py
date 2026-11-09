def localPeaks(rawData, localArea):
    n = len(rawData)
    up = [0] * n        # up[i]: strictly increasing steps ending at i
    for i in range(1, n):
        if rawData[i - 1] < rawData[i]:
            up[i] = up[i - 1] + 1
    down = [0] * n      # down[i]: strictly decreasing steps starting at i
    for i in range(n - 2, -1, -1):
        if rawData[i] > rawData[i + 1]:
            down[i] = down[i + 1] + 1
    return [i for i in range(n)
            if up[i] >= min(localArea, i) and down[i] >= min(localArea, n - 1 - i)]
