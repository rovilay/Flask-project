from flask import Flask, jsonify, request, Response, json
from temp_models import books

app = Flask(__name__)
app.config.from_envvar('APP_CONFIG')

def validate_book(book, patch_check=False):
    book_keys = list(book.keys())
    valid_keys = ['name', 'isbn', 'price']
    diff = set(valid_keys).intersection(book_keys) if patch_check else set(valid_keys).difference(book_keys)

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

@app.route('/')
def welcome():
    return 'Welcome to this flask app!'

@app.route('/books')
def get_books():
    response = Response(json.dumps({ 
            'message': 'Books retrieved Successfully',
            'success': True,
            'books': books
        }), status=200, mimetype='application/json')
    response.headers['Location'] = "/books"    
    return response

@app.route('/books/<int:id>')
def get_books_by_id(id):
    found_book = list(filter(lambda book : book['id'] == id, books))
    if found_book:
        response = Response(json.dumps({ 
            'message': 'Book retrieved Successfully',
            'success': True,
            'book': found_book[0]
        }), status=200, mimetype='application/json')
        response.headers['Location'] = "/books/" + str(id)
        return response
    else:
        response = Response(json.dumps({ 
            'message': 'No book matching this id',
            'success': False,
        }), status=404, mimetype='application/json')
        return response

@app.route('/books', methods=['POST'])
def add_books():
    new_book = request.get_json()
    valid_book = validate_book(new_book)

    if valid_book['is_valid']:
        last_book_index = len(books) - 1
        new_book['id'] = books[last_book_index]['id'] + 1
        book = {
                "id": new_book['id'],
                "name": new_book['name'],
                "price": new_book['price'],
                "isbn": new_book['isbn']
            }
        books.append(book)
        response = Response(json.dumps({ 
            'message': 'Book created Successfully',
            'success': True,
            'book': book
        }), status=201, mimetype='application/json')
        response.headers['Location'] = "/books/" + str(book['id'])
        return response
    else:
        props = ", ".join(valid_book['missing_props'])
        response = Response(json.dumps({
            'message': f'book parameter(s): {props} is/are missing',
            'success': False
        }), status=400, mimetype='application/json')
        response.headers['Location'] = "/books/" + str(book['id'])
        return response

@app.route('/books/<int:id>', methods=['PUT', 'PATCH'])
def update_books(id):
    book_update = request.get_json()
    patch_book = True if request.method == 'PATCH' else False
    valid_book = validate_book(book_update, patch_book)

    if valid_book['is_valid']:
        updated_book = update_book(id, book_update, books)

        if updated_book:
            response = Response(json.dumps({
                'message':'Update successful',
                'success': True,
                'book': updated_book
            }), status=200, mimetype='application/json')
            response.headers['Location'] = "/books/" + str(id)
            return response
        else:
            response = Response(json.dumps({
                'message': f'book with id: {id} was not found',
                'success': False
            }), status=404, mimetype='application/json')
            response.headers['Location'] = "/books/" + str(id)
            return response
    else:
        response = Response(json.dumps({
            'message': 'Book parameters must contain name, price and/or isbn',
            'success': False
        }), status=400, mimetype='application/json')
        response.headers['Location'] = "/books/" + str(id)
        return response

app.run(port=5000)
 