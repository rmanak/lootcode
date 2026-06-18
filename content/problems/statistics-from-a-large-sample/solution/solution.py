def sampleStats(count):
    total = sum(count)
    mn = next(k for k in range(256) if count[k] > 0)
    mx = next(k for k in range(255, -1, -1) if count[k] > 0)
    mean = sum(k * count[k] for k in range(256)) / total
    mode = max(range(256), key=lambda k: count[k])

    def kth(target):
        c = 0
        for k in range(256):
            c += count[k]
            if c >= target:
                return k

    if total % 2 == 1:
        median = float(kth(total // 2 + 1))
    else:
        median = (kth(total // 2) + kth(total // 2 + 1)) / 2
    return [float(mn), float(mx), round(mean, 5), round(median, 5), float(mode)]
