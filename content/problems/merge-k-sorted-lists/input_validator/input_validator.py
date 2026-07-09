"""Input-constraint validator for problem 'merge-k-sorted-lists'.

`validate_input(...)` returns True iff its arguments satisfy the input constraints
stated in the problem. Enforces: k range [0, 10^4], total length <= 10^4,
element types (int, not bool), and that each inner list is sorted in
non-decreasing (ascending) order — the problem states "k ascending lists"."""

def validate_input(lists):
    if not isinstance(lists, list):
        return False
    k = len(lists)
    if not (0 <= k <= 10**4):
        return False
    total_length = 0
    for lst in lists:
        if not isinstance(lst, list):
            return False
        total_length += len(lst)
        for x in lst:
            if not isinstance(x, int) or isinstance(x, bool):
                return False
        # Each inner list must be sorted in ascending (non-decreasing) order.
        for i in range(1, len(lst)):
            if lst[i] < lst[i - 1]:
                return False
    if not (total_length <= 10**4):
        return False
    return True
