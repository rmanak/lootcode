def sortList(head):
    vals = []
    node = head
    while node is not None:
        vals.append(node.val)
        node = node.next
    vals.sort()
    node = head
    for v in vals:
        node.val = v
        node = node.next
    return head
