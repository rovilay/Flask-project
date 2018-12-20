from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship, backref, join
from sqlalchemy.dialects import sqlite
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
    password = Column(String(80), nullable=False)
    books = relationship('Book', backref='user')

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
        if user:
            valid = check_password(_password, user.password)
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
    name = Column(String(80), nullable=False, unique=True)
    price = Column(Float, nullable=False)
    isbn = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    def json_response(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'isbn': self.isbn,
            'user_id': self.user_id
        }

    def add_book(self, _name, _price, _isbn, _user_id):
        try:
            new_book = Book(name=_name.lower(), price=_price,
                            isbn=_isbn, user_id=_user_id)
            db_session.add(new_book)
            db_session.commit()
            return Book.json_response(new_book)
        except IntegrityError as e:
            db_session.close()
            return Exception('Book with the same name already exist!')
        except Exception as e:
            db_session.close()
            return e

    def update_book(self, id, book_update_data, user_id):
        try:
            book_to_update = db_session.query(Book).filter_by(id=id).first()
            _book_to_update = Book.json_response(
                book_to_update) if book_to_update else None
            if _book_to_update and _book_to_update['user_id'] == user_id:
                book_to_update.name = book_update_data['name'] if "name" in book_update_data else book_to_update.name
                book_to_update.isbn = book_update_data['isbn'] if "isbn" in book_update_data else book_to_update.isbn
                book_to_update.price = book_update_data['price'] if "price" in book_update_data else book_to_update.price

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

    def get_all_books(self, personal=False, user_id=None):
        get_all = db_session.query(Book, User)\
            .select_from(join(User, Book))\
            .all()

        get_only_personal = db_session.query(Book, User)\
            .select_from(join(User, Book))\
            .filter_by(user_id=user_id)\
            .all()

        result = get_only_personal if personal is True else get_all

        c = [self._refine_book(response) for response in result] if len(
            result) > 0 else result
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
            'name': self.name,
            'price': self.price,
            'isbn': self.isbn
        }
        return json.dumps(book_object)
