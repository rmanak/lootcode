def reorderList(head):
    if head is None or head.next is None:
        return head
    # Find the middle (end of the first half).
    slow = fast = head
    while fast.next is not None and fast.next.next is not None:
        slow = slow.next
        fast = fast.next.next
    # Reverse the second half.
    second = slow.next
    slow.next = None
    prev = None
    while second is not None:
        second.next, prev, second = prev, second, second.next
    # Interleave the two halves.
    first, second = head, prev
    while second is not None:
        n1, n2 = first.next, second.next
        first.next = second
        second.next = n1
        first, second = n1, n2
    return head
