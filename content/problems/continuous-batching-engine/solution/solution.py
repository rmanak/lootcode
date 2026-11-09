from collections import deque


def runEngine(requests, batchSize, stopToken, vocabSize, continuous):
    queue = deque(range(len(requests)))
    slots = [None] * batchSize            # slot -> [request id, running sum, length, output]

    def fill():
        for s in range(batchSize):
            if slots[s] is None and queue:
                r = queue.popleft()
                prompt = requests[r][0]
                slots[s] = [r, sum(prompt), len(prompt), []]

    fill()
    finished, step = [], 0
    while any(slot is not None for slot in slots):
        step += 1
        for slot in slots:
            if slot is not None:
                tok = (31 * slot[1] + 7 * slot[2]) % vocabSize
                slot[1] += tok
                slot[2] += 1
                slot[3].append(tok)
        for s, slot in enumerate(slots):
            if slot is not None:
                r, out = slot[0], slot[3]
                if out[-1] == stopToken or len(out) == requests[r][1]:
                    finished.append([r, out, step])
                    slots[s] = None
        if continuous or all(slot is None for slot in slots):
            fill()
    return [finished, step]
