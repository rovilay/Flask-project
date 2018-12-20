def validate_book(book, patch_check=False):
    book_keys = list(book.keys())
    valid_keys = ['name', 'isbn', 'price']
    diff = set(valid_keys).intersection(book_keys) if patch_check else set(
        valid_keys).difference(book_keys)

    return {
        "is_valid": len(diff) > 0 if patch_check else len(diff) == 0,
        "missing_props": diff
    }


def update_book(id, book_update, books):
    updated_book = None
    for book in books:
        if book['id'] == id:
            book.update({
                "name": book_update["name"] if "name" in book_update else book["name"],
                "price": book_update["price"] if "price" in book_update else book["price"],
                "isbn": book_update["isbn"] if "isbn" in book_update else book["isbn"]
            })
            updated_book = book
            break

    return updated_book


def refine_book_data(book_data):
    try:
        valid_book_properties = ['name', 'isbn', 'price']
        refined_book = {key: value for key,
                        value in book_data.items() if key in valid_book_properties}
        return refined_book
    except Exception as e:
        return e