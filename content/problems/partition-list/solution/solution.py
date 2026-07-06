def partition(head, x):
    less = less_tail = ListNode(0)
    ge = ge_tail = ListNode(0)
    node = head
    while node is not None:
        if node.val < x:
            less_tail.next = node
            less_tail = node
        else:
            ge_tail.next = node
            ge_tail = node
        node = node.next
    ge_tail.next = None
    less_tail.next = ge.next
    return less.next
