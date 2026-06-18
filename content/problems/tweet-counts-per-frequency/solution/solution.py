def tweetCounts(freq, times, startTime, endTime):
    delta = {"minute": 60, "hour": 3600, "day": 86400}[freq]
    buckets = (endTime - startTime) // delta + 1
    res = [0] * buckets
    for tm in times:
        if startTime <= tm <= endTime:
            res[(tm - startTime) // delta] += 1
    return res
