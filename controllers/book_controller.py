from flask import Flask, jsonify, request, Response, json
from helpers.book_helpers import validate_book, refine_book_data
from helpers.user_helpers import authenticate
from helpers.__helpers import server_res, CustomException
from __models import Book as BookModel

Book = BookModel()


def get_all_books(secret_key):
    try:
        decoded_token = authenticate(secret_key)
        if 'message' and 'status' in decoded_token:
            response = server_res(
                decoded_token['message'], status=decoded_token['status']
            )
            return response
        else:
            personal = request.args.get('personal')
            if personal == '' or personal.lower() == 'false':
                all_books = Book.get_all_books()
                response = server_res('books retrieved successfully', success=True,
                                      status=200, book_data=all_books)
                return response
            elif personal.lower() == 'true':
                user_id = decoded_token['id']
                personal_books = Book.get_all_books(
                    personal=True, user_id=user_id)
                response = server_res('books retrieved successfully', success=True,
                                      status=200, book_data=personal_books)
                return response
            else:
                message = 'personal query can either be True or False'
                response = server_res(message, status=400)
                return response
    except Exception as e:

        response = server_res(str(e))
        return response


def get_books_by_id(secret_key, id):
    location = f'/books/{id}'
    try:
        decoded_token = authenticate(secret_key)
        if 'message' and 'status' in decoded_token:
            response = server_res(
                decoded_token['message'], status=decoded_token['status']
            )
            return response

        found_book = Book.get_book(id)
        if found_book:
            message = 'book retrieved successfully'
            response = server_res(message, success=True, book_data=found_book,
                                  status=200, location=location)
            return response
        else:
            message = f'No book matching this id: {id}'
            response = server_res(message, status=404, location=location)
            return response
    except Exception as e:
        return server_res(str(e), location=location)


def create_books(secret_key):
    try:
        decoded_token = authenticate(secret_key)
        if 'message' and 'status' in decoded_token:
            response = server_res(
                decoded_token['message'], status=decoded_token['status']
            )
            return response

        new_book_data = request.get_json()
        book = validate_book(new_book_data)

        if book['is_valid']:
            name = new_book_data['name']
            price = new_book_data['price']
            isbn = new_book_data['isbn']
            user_id = decoded_token['id']
            new_book = Book.add_book(name, price, isbn, user_id)
            book_err_msg = 'Book with the same name already exist!'
            if isinstance(new_book, Exception) and str(new_book) == book_err_msg:
                raise CustomException(book_err_msg, status=409)
            else:
                response = server_res('book created successfully',
                                      success=True, book_data=new_book, status=201)
                return response
        else:
            props = ", ".join(book['missing_props'])
            response = server_res(
                f'book parameter(s): {props} is/are missing', status=400)
            return response
    except CustomException as e:
        response = server_res(e.message, status=e.status)
        return response
    except Exception as e:
        return server_res(str(e))


def modify_books(secret_key, id):
    location = f'/books/{id}'
    try:
        decoded_token = authenticate(secret_key)
        if 'message' and 'status' in decoded_token:
            response = server_res(
                decoded_token['message'], status=decoded_token['status']
            )
            return response

        book_update_data = request.get_json()
        patch_book = True if request.method == 'PATCH' else False
        refined_book = refine_book_data(book_update_data)
        book = validate_book(refined_book, patch_book)
        response = None
        if book['is_valid']:
            user_id = decoded_token['id']
            updated_book = Book.update_book(id, refined_book, user_id)
            if updated_book and updated_book != 403:
                message = 'Update successful'
                response = server_res(message, status=200, success=True,
                                      book_data=updated_book, location=location)
            elif updated_book and updated_book == 403:
                message = f'This book does not belong to you!'
                response = server_res(message, status=403, location=location)
            else:
                message = f'book with id: {id} was not found'
                response = server_res(message, status=404, location=location)
        else:
            message = 'Book parameters must contain name, price and/or isbn'
            response = server_res(message, status=400, location=location)
        return response
    except Exception as e:
        return server_res(str(e))


def remove_books(secret_key, id):
    location = f'/books/{id}'
    try:
        decoded_token = authenticate(secret_key)
        if 'message' and 'status' in decoded_token:
            response = server_res(
                decoded_token['message'], status=decoded_token['status']
            )
            return response

        user_id = decoded_token['id']
        book_deleted = Book.delete_book(id, user_id)
        response = None
        if book_deleted is True:
            message = 'Delete successful'
            response = server_res(message, status=200, location=location)
        elif book_deleted == 403:
            message = f'This book does not belong to you'
            response = server_res(message, status=403, location=location)
        else:
            message = f'book with id: {id} was not found'
            response = server_res(message, status=404, location=location)
        return response
    except Exception as e:
        return server_res(str(e))
