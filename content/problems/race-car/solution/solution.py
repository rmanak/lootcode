def racecar(target):
    from collections import deque
    q = deque([(0, 1)])
    seen = {(0, 1)}
    steps = 0
    while q:
        for _ in range(len(q)):
            pos, speed = q.popleft()
            if pos == target:
                return steps
            np_, ns = pos + speed, speed * 2
            if (np_, ns) not in seen and abs(np_) <= 2 * target:
                seen.add((np_, ns))
                q.append((np_, ns))
            ns2 = -1 if speed > 0 else 1
            if (pos, ns2) not in seen:
                seen.add((pos, ns2))
                q.append((pos, ns2))
        steps += 1
    return -1
