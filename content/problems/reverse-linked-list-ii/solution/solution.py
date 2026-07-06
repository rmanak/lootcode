def reverseBetween(head, m, n):
    dummy = ListNode(0, head)
    prev = dummy
    for _ in range(m - 1):
        prev = prev.next
    cur = prev.next
    for _ in range(n - m):
        nxt = cur.next
        cur.next = nxt.next
        nxt.next = prev.next
        prev.next = nxt
    return dummy.next
