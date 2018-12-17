from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json
from settings import app

db = SQLAlchemy(app)

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    isbn = db.Column(db.Integer, nullable=False)

    def json_response(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'isbn': self.isbn
        }

    def add_book(self, _name, _price, _isbn):
        new_book = Book(name=_name, price=_price, isbn=_isbn)
        db.session.add(new_book)
        db.session.commit()
        return Book.json_response(new_book)
    
    def update_book(self, id, book_update_data):
        book_to_update = Book.query.filter_by(id=id).first()
        if book_to_update:
            book_to_update.name = book_update_data['name'] if "name" in book_update_data else book_to_update.name,
            book_to_update.isbn = book_update_data['isbn'] if "isbn" in book_update_data else book_to_update.isbn,
            book_to_update.price = book_update_data['isbn'] if "isbn" in book_update_data else book_to_update.isbn,
            db.session.commit()
            return Book.json_response(book_to_update)

    def delete_book(self, id):
        book = Book.query.filter_by(id=id).first()
        if book:
            db.session.delete(book)
            db.session.commit()
            return True
        else:
            return False
    def get_all_books(self):
        return [Book.json_response(book) for book in Book.query.all()]
    
    def get_book(self, id):
        book = Book.query.filter_by(id=id).first()
        return Book.json_response(book) if book else None
    
    def __repr__(self):
        book_object = {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'isbn': self.isbn
        }
        return json.dumps(book_object)
