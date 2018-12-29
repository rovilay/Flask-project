from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship, backref, join, joinedload, load_only
from sqlalchemy.dialects import sqlite
from datetime import datetime
import json
from __init_models import Base, DB_session
from helpers.__helpers import hash_password, check_password

db_session = DB_session()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    firstname = Column(String(80), nullable=False)
    lastname = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False, unique=True)
    password = Column(String(225), nullable=False)
    books = relationship('Book', backref='user')
    fav_books = relationship('Book', backref=backref(
        'favourites', lazy='select'), secondary='favourites')

    def json_response(self):
        return {
            'id': self.id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email
        }

    def add_user(self, _firstname, _lastname, _email, _password):
        try:
            password = hash_password(_password)
            print('pass===++++ ', password)
            new_user = User(firstname=_firstname, lastname=_lastname,
                            email=_email.lower(), password=password)
            db_session.add(new_user)
            db_session.commit()
            return User.json_response(new_user)
        except IntegrityError as e:
            db_session.close()
            return Exception('Email already exist')
        except Exception as e:
            db_session.close()
            return e

    def delete_user(self, id):
        user = db_session.query(User).filter_by(id=id).first()
        if user:
            db_session.delete(user)
            db_session.commit()
            return True
        else:
            return False

    def get_all_users(self):
        return [User.json_response(user) for user in db_session.query(User).all()]

    def get_user(self, id):
        user = db_session.query(User).filter_by(id=id).first()
        return User.json_response(user) if user else None

    def check_user_password(self, _email, _password):
        user = db_session.query(User)\
            .filter_by(email=_email.lower())\
            .first()
        print('valid====', _password)

        if user:
            valid = check_password(_password, user.password)
            print('valid====', valid)
            res = User.json_response(user) if valid else False
            return res
        else:
            return None

    def check_user_id(self, _email, _id):
        user = db_session.query(User).filter_by(email=_email.lower())\
            .filter_by(id=_id).first()
        res = User.json_response(user) if user else False
        return res

    def __repr__(self):
        user_object = {
            'id': self.id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email,
            'password': self.password
        }
        return json.dumps(user_object)


class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(80), nullable=False, unique=True)
    price = Column(Float, nullable=False)
    isbn = Column(Integer, nullable=False)
    image = Column(String(225), nullable=False,
                   default="https://res.cloudinary.com/rovilay/image/upload/v1546053854/book-demo.jpg")
    image_name = Column(String(80), nullable=False, default="book-demo")
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    fav_users = relationship('User', backref=backref(
        'favourites',  lazy='joined'), secondary='favourites', lazy='joined')

    def json_response(self):
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'isbn': self.isbn,
            'image': self.image,
            'image_name': self.image_name,
            'user_id': self.user_id
        }

    def add_book(self, _title, _price, _isbn, _user_id, _image, _image_name=None):
        try:
            default_image_name = _title + '_' + str(_isbn)
            image_name = _image_name if _image_name else default_image_name
            new_book = Book(title=_title.lower(), price=_price,
                            isbn=_isbn, user_id=_user_id, image=_image, image_name=image_name)
            db_session.add(new_book)
            db_session.commit()
            return Book.json_response(new_book)
        except IntegrityError as e:
            db_session.close()
            return Exception('Book with the same title already exist!')
        except Exception as e:
            db_session.close()
            return e

    def update_book(self, id, book_update_data, user_id):
        try:
            book_to_update = db_session.query(Book).filter_by(id=id).first()
            _book_to_update = Book.json_response(
                book_to_update) if book_to_update else None
            if _book_to_update and _book_to_update['user_id'] == user_id:
                book_to_update.title = book_update_data['title'] if "title" in book_update_data else book_to_update.title
                book_to_update.isbn = book_update_data['isbn'] if "isbn" in book_update_data else book_to_update.isbn
                book_to_update.price = book_update_data['price'] if "price" in book_update_data else book_to_update.price
                book_to_update.image = book_update_data['image'] if "image" in book_update_data else book_to_update.image
                book_to_update.image_name = book_update_data[
                    'image_name'] if "image_name" in book_update_data else book_to_update.image_name

                db_session.commit()
                return Book.json_response(book_to_update)
            elif _book_to_update and _book_to_update['user_id'] != user_id:
                return 403
            else:
                return False
        except Exception as e:
            return e

    def delete_book(self, id, user_id):
        try:
            book = db_session.query(Book).filter_by(id=id).first()
            _book = Book.json_response(book) if book else None
            if _book and _book['user_id'] == user_id:
                db_session.delete(book)
                db_session.commit()
                return True
            elif _book and _book['user_id'] != user_id:
                return 403
            else:
                return False
        except Exception as e:
            db_session.close()
            return e

    def favourite_book(self, id, user_id):
        try:
            book = db_session.query(Book).filter_by(id=id).first()
            user = db_session.query(User).filter_by(id=user_id).first()
            if book and user:
                a = book.favourites.append(user)
                db_session.commit()
                return True
            else:
                return False
        except Exception as e:
            db_session.close()
            print('error occurred in favourite', e)
            return e

    def remove_favourite_book(self, id, user_id):
        try:
            book = db_session.query(Book).filter_by(id=id).first()
            user = db_session.query(User).filter_by(id=user_id).first()
            if book and user:
                book.favourites.remove(user)
                db_session.commit()
                return True
            else:
                return False
        except Exception as e:
            db_session.close()
            return e

    def get_all_fav_books(self, user_id):
        try:
            user = db_session.query(User).filter_by(id=user_id).first()
            fav_books = user.favourites
            a = list(fav_books)
            return a

        except Exception as e:
            db_session.close()
            return e

    def _refine_book(self, book_tuple):
        user_props_to_remove = ('email',)
        book_props_to_remove = ('user_id',)

        _book = Book.json_response(book_tuple[0])
        _user = User.json_response(book_tuple[1])

        refined_book = {key: value for key, value in _book.items(
        ) if key not in book_props_to_remove}
        refined_user = {key: value for key, value in _user.items(
        ) if key not in user_props_to_remove}

        refined_book.update({'user': refined_user})
        return refined_book

    def _add_favs(self, books, fav_books):
        a = {'favourite': True}
        c = books.copy()
        fav_ids = [book.id for book in fav_books]

        for book in c:
            if book['id'] in fav_ids:
                book.update(a)

        return c

    def get_all_books(self, personal=False, user_id=None):
        result = None
        if personal is True:
            result = db_session.query(Book, User)\
                .select_from(join(User, Book))\
                .filter_by(user_id=user_id)\
                .all()
        else:
            result = db_session.query(Book, User)\
                .select_from(join(User, Book))\
                .all()

        fav_books = self.get_all_fav_books(user_id)

        c = [self._refine_book(response) for response in result] if len(
            result) > 0 else result

        f = self._add_favs(books=c, fav_books=fav_books)

        return c

    def get_book(self, id):
        result = db_session.query(Book, User)\
            .select_from(join(User, Book))\
            .filter_by(id=id)\
            .first()

        if result:
            book = Book.json_response(result[0])
            user = User.json_response(result[1])
            c = self._refine_book(result)
            return c
        else:
            return None

    def __repr__(self):
        book_object = {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'isbn': self.isbn,
            'image': self.image,
            'image_name': self.image_name
        }
        return json.dumps(book_object)


class Favourite(Base):
    __tablename__ = 'favourites'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
