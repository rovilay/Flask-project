from flask import Flask
from functools import wraps
from controllers.user_controller import signup_user, login_user
from controllers.book_controller import get_all_books, get_books_by_id,\
    create_books, modify_books, remove_books, fav_book, del_fav_book, get_all_fav_books
# from decorators.auth import auth_user
from settings import app

secret_key = app.config['SECRET_KEY']


# def auth_user(f):
#     @wraps(f)
#     def decorated_auth():
#         print('I am here')
#         f()
#         print('after')
#     return decorated_auth

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


@app.route('/books/favourites', methods=['GET'])
def get_fav_books():
    return get_all_fav_books(secret_key)


@app.route('/books/<int:id>/favourites', methods=['POST'])
def fav_books(id):
    return fav_book(secret_key, id)


@app.route('/books/<int:id>/favourites', methods=['DELETE'])
def remove_fav_books(id):
    return del_fav_book(secret_key, id)


app.run(port=5000)
