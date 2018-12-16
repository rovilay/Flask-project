from flask import Flask, jsonify, request, Response, json
from temp_models import books

app = Flask(__name__)
app.config.from_envvar('APP_CONFIG')

def validate_book(book):
    book_keys = list(book.keys())
    valid_keys = ['name', 'isbn', 'price']
    diff = set(valid_keys).difference(book_keys)
    return {
        "is_valid": len(diff) == 0,
        "missing_props": diff
    }

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
        return response

app.run(port=5000)
