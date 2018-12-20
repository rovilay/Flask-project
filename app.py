from flask import Flask
from controllers.user_controller import signup_user, login_user
from controllers.book_controller import get_all_books, get_books_by_id, create_books, modify_books, remove_books
from settings import app

secret_key = app.config['SECRET_KEY']


@app.route('/')
def welcome():
    return 'Welcome to this flask app!'


@app.route('/signup', methods=['POST'])
def signup():
    return signup_user(secret_key)


@app.route('/login', methods=['POST'])
def login():
    return login_user(secret_key)


@app.route('/books')
def get_books():
    return get_all_books(secret_key)


@app.route('/books/<int:id>')
def get_book(id):
    return get_books_by_id(secret_key, id)


@app.route('/books', methods=['POST'])
def add_books():
    return create_books(secret_key)


@app.route('/books/<int:id>', methods=['PUT', 'PATCH'])
def update_books(id):
    return modify_books(secret_key, id)


@app.route('/books/<int:id>', methods=['DELETE'])
def delete_books(id):
    return remove_books(secret_key, id)


app.run(port=5000)
