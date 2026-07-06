def reverseList(head):
    prev = None
    while head is not None:
        head.next, prev, head = prev, head, head.next
    return prev
