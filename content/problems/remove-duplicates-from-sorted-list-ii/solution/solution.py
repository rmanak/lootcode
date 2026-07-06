def deleteDuplicates(head):
    dummy = ListNode(0, head)
    prev = dummy
    cur = head
    while cur is not None:
        if cur.next is not None and cur.val == cur.next.val:
            v = cur.val
            while cur is not None and cur.val == v:
                cur = cur.next
            prev.next = cur
        else:
            prev = cur
            cur = cur.next
    return dummy.next
