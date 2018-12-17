from flask import Flask, jsonify, request, Response, json
from temp_models import books
from settings import app
from book_model import Book as BookModel

Book = BookModel()

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
    all_books = Book.get_all_books()
    response = Response(
        json.dumps({
            'message': 'books retrieved successfully',
            'success': True,
            'books': all_books
        }), status=200, mimetype='application/json'
    )
    response.headers['Location'] = "/books"    
    return response

@app.route('/books/<int:id>')
def get_books_by_id(id):
    found_book = Book.get_book(id)
    if found_book:
        response = Response(
            json.dumps({
            'message': 'book retrieved successfully',
            'success': True,
            'book': found_book
        }), status=200, mimetype='application/json'
        )
        response.headers['Location'] = "/books/" + str(id)
        return response
    else:
        response = Response(json.dumps({ 
            'message': f'No book matching this id: {id}',
            'success': False,
        }), status=404, mimetype='application/json')
        response.headers['Location'] = "/books/" + str(id)
        return response

@app.route('/books', methods=['POST'])
def add_books():
    new_book_data = request.get_json()
    valid_book = validate_book(new_book_data)

    if valid_book['is_valid']:
        name = new_book_data['name']
        price = new_book_data['price']
        isbn = new_book_data['isbn']

        new_book = Book.add_book(name, price, isbn)
        response = Response(json.dumps({
            'message': 'book created successfully',
            'success': True,
            'book': new_book
        }), status=201, mimetype='application/json'
        )
        response.headers['Location'] = "/books/" + str(id)
        return response
    else:
        props = ", ".join(valid_book['missing_props'])
        response = Response(json.dumps({
            'message': f'book parameter(s): {props} is/are missing',
            'success': False
        }), status=400, mimetype='application/json')
        response.headers['Location'] = "/books/" + str(id)
        return response

@app.route('/books/<int:id>', methods=['PUT', 'PATCH'])
def update_books(id):
    book_update_data = request.get_json()
    print('<<<<<>>>>>>', book_update_data)
    patch_book = True if request.method == 'PATCH' else False
    valid_book = validate_book(book_update_data, patch_book)

    if valid_book['is_valid']:
        updated_book = Book.update_book(id, book_update_data)
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

@app.route('/books/<int:id>', methods=['DELETE'])
def delete_books(id):
    book_deleted = Book.delete_book(id)
    if book_deleted:
        response = Response(json.dumps({
        'message':'Delete successful',
        'success': True,
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

app.run(port=5000)
 