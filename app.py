from flask import Flask, jsonify
from temp_models import books

app = Flask(__name__)
print(__name__)

@app.route('/')
def welcome():
    return 'Welcome to this flask app!'

@app.route('/books')
def get_books():
    return jsonify({ 'books': books, 'success': True })

@app.route('/books/<int:id>')
def get_books_by_id(id):
    found_book = None
    for book in books:
        if book['id'] == id:
            found_book = book
            break
        
    if found_book is None:
        return jsonify({ 'message': 'No book matching this id', 'success': False })
    else:
        return jsonify({ 'book': found_book, 'success': True })


app.run(port=5000)
