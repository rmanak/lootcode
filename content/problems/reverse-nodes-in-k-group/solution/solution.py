def reverseKGroup(head, k):
    dummy = ListNode(0, head)
    group_prev = dummy
    while True:
        # Find the k-th node from group_prev; stop if fewer than k remain.
        kth = group_prev
        for _ in range(k):
            kth = kth.next
            if kth is None:
                return dummy.next
        group_next = kth.next
        # Reverse the group in place.
        prev, cur = group_next, group_prev.next
        while cur is not group_next:
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt
        # Reconnect: group_prev -> kth (new head) ... old head -> group_next.
        tmp = group_prev.next
        group_prev.next = kth
        group_prev = tmp
