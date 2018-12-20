from flask import Flask, jsonify, request, Response, json
from helpers.user_helpers import validate_user_names, validate_email_password, get_token, authenticate
from helpers.__helpers import server_res, CustomException
from __models import User as UserModel

User = UserModel()


def signup_user(secret_key):
    location = '/signup'
    try:
        user_data = request.get_json()
        if isinstance(user_data, dict):
            init_errors = validate_user_names(user_data)
            errors = validate_email_password(user_data, errors_obj=init_errors)
            if bool(errors):
                message = str(errors)
                raise CustomException(message, status=400)
            else:
                firstname = user_data['firstname']
                lastname = user_data['lastname']
                email = user_data['email']
                password = user_data['password']

                new_user = User.add_user(firstname, lastname, email, password)
                if isinstance(new_user, Exception) and str(new_user) == 'Email already exist':
                    message = 'Email already exist'
                    raise CustomException(message, status=409)
                elif isinstance(new_user, Exception):
                    raise Exception(str(new_user))
                else:
                    token = get_token(secret_key, new_user)
                    response = server_res('Signup successful!', success=True,
                                          status=201, location='/login', token=str(token))
                    return response

        else:
            message = 'User data not in correct format'
            raise CustomException(message, status=400)
    except CustomException as e:
        response = server_res(e.message, status=e.status, location='/login')
        return response
    except Exception as e:
        response = server_res(str(e), location=location)
        return response


def login_user(secret_key):
    try:
        user_data = request.get_json()
        if isinstance(user_data, dict) and ('email' and 'password' in user_data):
            email = user_data['email']
            password = user_data['password']
            confirm_user = User.check_user_password(email, password)
            if isinstance(confirm_user, dict) and ('email' in confirm_user):
                token = get_token(secret_key, confirm_user)
                response = server_res('Login successful!',
                                      status=200, location='/login', token=str(token))
                return response
            else:
                message = 'Invalid Email or Password!'
                raise CustomException(message, status=400)
        else:
            raise CustomException(
                'User credentials must contain email and password', status=400)
    except CustomException as e:
        response = server_res(e.message, status=e.status, location='/login')
        return response
    except Exception as e:
        response = server_res(str(e), location='/login')
        return response
