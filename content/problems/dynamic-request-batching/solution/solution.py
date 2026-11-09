from collections import deque


def batchRequests(arrivals, maxBatchSize, maxWaitMs, setupMs, perItemMs):
    n = len(arrivals)
    queue = deque()
    free_at = 0
    nxt = 0
    batches, finish = [], [0] * n
    while nxt < n or queue:
        if queue:
            if len(queue) >= maxBatchSize:
                ready = arrivals[queue[maxBatchSize - 1]]     # the moment the batch filled up
            else:
                ready = arrivals[queue[0]] + maxWaitMs        # the oldest request's deadline
            send = max(free_at, ready)
        else:
            send = None
        # Arrivals up to (and at) the send time join first; they may fill the batch sooner.
        if nxt < n and (send is None or arrivals[nxt] <= send):
            queue.append(nxt)
            nxt += 1
            continue
        batch = [queue.popleft() for _ in range(min(maxBatchSize, len(queue)))]
        free_at = send + setupMs + len(batch) * perItemMs
        for i in batch:
            finish[i] = free_at
        batches.append([send, batch])
    return [batches, finish]
