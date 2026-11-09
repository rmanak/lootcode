An LLM inference server decodes many requests at once: each **step** runs the
model once over a batch of up to `batchSize` sequences and produces one new
token for each. Requests finish at different times. **Static batching** waits
until the whole batch is done before starting new requests, leaving finished
slots idle. **Continuous batching** (as in vLLM and TGI) refills a slot as soon
as its request finishes. Simulate an engine that does either.

`requests[r]` is `[prompt, maxTokens]`: request $r$'s prompt tokens and the
most tokens it may generate. The **model** is a stand-in, a fixed function of
a row's whole sequence (prompt followed by the tokens generated so far):

$$
\operatorname{next}(x_1, \dots, x_L) = \Big( 31 \sum_{k=1}^{L} x_k + 7L \Big) \bmod V
$$

with $V$ = `vocabSize`. Every row's next token is computed independently, so
batching never changes *which* tokens a request gets, only *when* it finishes.

**The engine.** There are `batchSize` slots, numbered from $0$, and a queue of
waiting requests in order $0, 1, 2, \dots$.

1. **Fill**: before the first step, move requests from the queue into the
   slots in increasing slot order.
2. **Step** (steps are numbered from $1$): every occupied slot gets the next
   token for its row, appended to that request's output.
3. **Finish**: going through the slots in increasing order, a request is done
   if the token just produced is `stopToken` (it stays in the output) or its
   output has reached `maxTokens` tokens. Record it as finished at this step
   and free its slot.
4. **Refill**: with `continuous` true, fill every free slot from the queue, in
   increasing slot order. With `continuous` false, refill only when **all**
   slots are free (then fill them as in step 1).
5. Repeat from 2 while any slot is occupied.

**Return `[finished, steps]`**: `finished` lists `[requestId, outputTokens,
finishStep]` for every request in the order they finished (within one step,
in slot order), and `steps` is the total number of model calls.

## Constraints

- `1 <= len(requests) <= 500`, `1 <= batchSize <= 64`
- Every prompt has `1` to `50` tokens, each in `[0, vocabSize)`
- `1 <= maxTokens <= 200`
- `2 <= vocabSize <= 1000` and `0 <= stopToken < vocabSize`

## Examples

**Example 1**
```
Input:  requests = [[[1], 3], [[2], 5], [[3], 2]], batchSize = 2, stopToken = 9, vocabSize = 10, continuous = true
Output: [[[1, [9], 1], [0, [8, 3, 3], 3], [2, [0, 7], 3]], 3]
Explanation: requests 0 and 1 start in slots 0 and 1. Request 1's first token
is (31·2 + 7·1) mod 10 = 9, the stop token, so it finishes at step 1 and
request 2 takes its slot. Request 0 reaches its 3 tokens at step 3, and so
does request 2 with its 2 tokens.
```

**Example 2**
```
Input:  requests = [[[1], 3], [[2], 5], [[3], 2]], batchSize = 2, stopToken = 9, vocabSize = 10, continuous = false
Output: [[[1, [9], 1], [0, [8, 3, 3], 3], [2, [0, 7], 5]], 5]
Explanation: the same requests with static batching. Slot 1 sits idle after
step 1 until request 0 finishes at step 3; request 2 then runs at steps 4
and 5.
```

**Example 3**
```
Input:  requests = [[[4], 1], [[0, 5], 3], [[2, 2], 2]], batchSize = 2, stopToken = 0, vocabSize = 8, continuous = true
Output: [[[0, [3], 1], [2, [2, 7], 3], [1, [1, 7, 7], 3]], 3]
Explanation: request 0 finishes after one token and request 2 moves into
slot 0. At step 3 both remaining requests finish; request 2 is in slot 0, so
it is listed first.
```
