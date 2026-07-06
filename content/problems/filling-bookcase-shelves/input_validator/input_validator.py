"""Input-constraint validator for problem 'filling-bookcase-shelves'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(books, shelfWidth):
    if not isinstance(books, list):
        return False
    if isinstance(shelfWidth, bool) or not isinstance(shelfWidth, int):
        return False
    if len(books) < 1 or len(books) > 1000:
        return False
    if shelfWidth < 1 or shelfWidth > 1000:
        return False
    for book in books:
        if not isinstance(book, list):
            return False
        if len(book) != 2:
            return False
        thickness = book[0]
        height = book[1]
        if isinstance(thickness, bool) or not isinstance(thickness, int):
            return False
        if isinstance(height, bool) or not isinstance(height, int):
            return False
        if thickness < 1 or thickness > shelfWidth:
            return False
        if height < 1 or height > 1000:
            return False
    return True
