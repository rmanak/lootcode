A GPU serves a model far more efficiently on a batch of requests than one at a
time, but holding requests back to build a batch adds latency. Inference
servers resolve this with **dynamic batching**: a batch is sent as soon as it
is full, or once its oldest request has waited long enough. Simulate one such
server, in whole milliseconds.

`arrivals[i]` is the time request $i$ arrives; the list is sorted in
non-decreasing order. Requests wait in a FIFO queue. There is a single worker.
A batch of $s$ requests sent at time $t$ keeps the worker busy until
$t + \texttt{setupMs} + s \cdot \texttt{perItemMs}$, which is also when every
request in it finishes. The worker can start a new batch at that same instant.

The server sends a batch at the **earliest** time $t$ at which all of these
hold:

1. the worker is free;
2. the queue is not empty;
3. the queue holds at least `maxBatchSize` requests, **or** the request at the
   front of the queue arrived at or before $t - \texttt{maxWaitMs}$.

The batch is the first `min(maxBatchSize, queue length)` requests of the
queue. Requests that arrive at time $t$ join the queue **before** the server
decides what to send at $t$.

Note that the wait is measured from the **oldest** queued request, not the
newest (a timer that restarted on every arrival would let a steady trickle of
requests starve the queue), and that while the worker is busy the queue keeps
filling, so the next batch can go out full the moment the worker is free.

**Return `[batches, finish]`**: `batches` lists every batch in the order sent,
as `[sendTime, indices]` with the request indices in queue order, and
`finish[i]` is the time request $i$ finishes.

## Constraints

- `1 <= len(arrivals) <= 3000`; `0 <= arrivals[i] <= 10⁶`, sorted non-decreasing
- `1 <= maxBatchSize <= 64`
- `0 <= maxWaitMs, setupMs <= 10⁴`; `0 <= perItemMs <= 10³`

## Examples

**Example 1**
```
Input:  arrivals = [0, 1, 2, 10, 11, 30], maxBatchSize = 3, maxWaitMs = 5, setupMs = 2, perItemMs = 1
Output: [[[2, [0, 1, 2]], [15, [3, 4]], [35, [5]]], [7, 7, 7, 19, 19, 38]]
Explanation: the queue is full at time 2, and the batch takes 2 + 3·1 = 3 ms.
Requests 3 and 4 never fill a batch, so they go when request 3 has waited
5 ms (time 15) and finish at 15 + 2 + 2 = 19. Request 5 goes alone at 35.
```

**Example 2**
```
Input:  arrivals = [0, 0, 0, 0, 0, 1, 2], maxBatchSize = 2, maxWaitMs = 100, setupMs = 10, perItemMs = 0
Output: [[[0, [0, 1]], [10, [2, 3]], [20, [4, 5]], [102, [6]]], [10, 10, 20, 20, 30, 30, 112]]
Explanation: the worker is busy for 10 ms per batch, and full batches leave
whenever it frees up. Request 6 is then alone and waits its full 100 ms.
```

**Example 3**
```
Input:  arrivals = [5, 7, 9, 11, 13, 15], maxBatchSize = 4, maxWaitMs = 6, setupMs = 0, perItemMs = 3
Output: [[[11, [0, 1, 2, 3]], [23, [4, 5]]], [23, 23, 23, 23, 29, 29]]
Explanation: at time 11 request 0's wait runs out, but request 3 arrives at
that same instant and joins first, so a full batch of 4 goes. Requests 4 and
5 are due at 19, but the worker is busy until 23.
```
