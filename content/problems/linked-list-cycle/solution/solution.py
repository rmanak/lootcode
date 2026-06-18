def hasCycle(head, pos):
    n = len(head)
    if n == 0:
        return False
    nxt = list(range(1, n)) + [pos]
    slow = fast = 0
    while True:
        fast = nxt[fast]
        if fast == -1:
            return False
        fast = nxt[fast]
        if fast == -1:
            return False
        slow = nxt[slow]
        if slow == fast:
            return True
