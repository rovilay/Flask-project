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
            user_id = decoded_token['id']

            if personal is None or personal == '' or personal.lower() == 'false':
                all_books = Book.get_all_books(user_id=user_id)
                response = server_res('books retrieved successfully', success=True,
                                      status=200, book_data=all_books)
                return response
            elif personal.lower() == 'true':
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
            title = new_book_data['title']
            price = new_book_data['price']
            isbn = new_book_data['isbn']
            user_id = decoded_token['id']
            image = new_book_data['image'] if "image" in new_book_data and new_book_data['image'] != "" else None
            new_book = Book.add_book(title, price, isbn, user_id, image)
            book_err_msg = 'Book with the same title already exist!'
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
            message = 'Book parameters must contain title, price and/or isbn'
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


def fav_book(secret_key, id):
    location = f'/books/{id}/favourites'
    try:
        decoded_token = authenticate(secret_key)
        if 'message' and 'status' in decoded_token:
            response = server_res(
                decoded_token['message'], status=decoded_token['status']
            )
            return response

        user_id = decoded_token['id']
        favourite_book = Book.favourite_book(id, user_id)
        a = json.loads(str(favourite_book))
        a.update({'favourite': True})
        response = None
        if favourite_book:
            message = 'Book added as favourite'
            response = server_res(message, status=200,
                                  location=location, book_data=a)
        else:
            message = f'book with id: {id} was not found'
            response = server_res(message, status=404, location=location)
        return response
    except Exception as e:
        return server_res(str(e))


def del_fav_book(secret_key, id):
    location = f'/books/{id}/favourites'
    try:
        decoded_token = authenticate(secret_key)
        if 'message' and 'status' in decoded_token:
            response = server_res(
                decoded_token['message'], status=decoded_token['status']
            )
            return response

        user_id = decoded_token['id']
        remove_fav_book = Book.remove_favourite_book(id, user_id)
        response = None
        if remove_fav_book is True:
            message = 'Book removed as favourite'
            response = server_res(message, status=200, location=location)
        elif remove_fav_book is False:
            message = f'book with id: {id} was not found'
            response = server_res(message, status=404, location=location)
        else:
            message = 'Book not in your favourites'
            response = server_res(message, status=400, location=location)
        return response
    except Exception as e:
        return server_res(str(e))


def get_all_fav_books(secret_key):
    location = f'/books/favourites'
    try:
        decoded_token = authenticate(secret_key)
        if 'message' and 'status' in decoded_token:
            response = server_res(
                decoded_token['message'], status=decoded_token['status']
            )
            return response

        user_id = decoded_token['id']
        all_fav_books = Book.get_all_fav_books(user_id)
        a = json.loads(str(all_fav_books))
        for book in a:
            book.update({'favourite': True})

        response = None
        if len(all_fav_books) >= 0:
            message = 'your favourite books retrieved successfully'
            response = server_res(message, status=200, success=True,
                                  location=location, book_data=a)
        return response
    except Exception as e:
        return server_res(str(e), location=location)
