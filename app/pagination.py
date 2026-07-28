"""Pagination helpers shared by the paginated lists.

Lives here rather than in a router because both the public problem list
(``routers/pages.py``) and the admin table (``routers/admin_problems.py``) need
it, and a router importing another router's private was the only thing holding
them together.
"""
from __future__ import annotations


def page_window(page: int, pages: int, span: int = 2) -> list[int | None]:
    """Page numbers to show, with `None` marking an ellipsis gap.

    Always includes the first/last page and a small window around `page`,
    e.g. [1, None, 4, 5, 6, None, 20]."""
    if pages <= 7:
        return list(range(1, pages + 1))
    wanted = {1, pages, page}
    for d in range(1, span + 1):
        wanted.add(page - d)
        wanted.add(page + d)
    items: list[int | None] = []
    prev = 0
    for n in sorted(n for n in wanted if 1 <= n <= pages):
        if n - prev > 1:
            items.append(None)
        items.append(n)
        prev = n
    return items
