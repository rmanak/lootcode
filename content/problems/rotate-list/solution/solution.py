def rotateRight(head, k):
    if head is None or head.next is None:
        return head
    # Measure length and find the tail.
    n = 1
    tail = head
    while tail.next is not None:
        tail = tail.next
        n += 1
    k %= n
    if k == 0:
        return head
    tail.next = head  # close into a ring
    new_tail = head
    for _ in range(n - k - 1):
        new_tail = new_tail.next
    new_head = new_tail.next
    new_tail.next = None
    return new_head
