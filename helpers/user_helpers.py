from flask import request
from datetime import datetime, timedelta
import jwt
import re
from .__helpers import server_res, CustomException, refine_token
from __models import User as UserModel

User = UserModel()


def validate_user_names(user_data, errors_obj={}):
    try:
        user_is_valid = False
        errors = errors_obj
        user_keys = list(user_data.keys())
        valid_keys = ['firstname', 'lastname']
        common_keys = set(valid_keys).intersection(user_keys)

        if len(common_keys) != 2:
            errors['names'] = 'firstname and lastname are required!'

        int_reg = re.compile(r"(^\d$)")
        for key in list(common_keys):
            val = user_data[key]

            # checks if integer is in title
            if int_reg.search(val) is not None:
                errors[key] = f'firstname and lastname must not contain numbers'

        return errors
    except Exception as e:
        return e


def validate_email_password(user_data, errors_obj={}):
    try:
        user_is_valid = False
        errors = errors_obj
        user_keys = list(user_data.keys())
        valid_keys = ['email', 'password']
        common_keys = set(valid_keys).intersection(user_keys)

        if len(common_keys) != 2:
            errors['data'] = 'email and password are required!'

        email_reg = re.compile(
            r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

        for key in list(common_keys):
            if key == 'email' and email_reg.match(user_data[key]) is None:
                errors[key] = f'email is not valid'
            if key == 'password' and len(str(user_data[key])) < 7:
                errors[key] = 'password must not be less than 7 characters'
        return errors
    except Exception as e:
        return e


def get_token(secret_key, payload={},):
    try:
        expiration_date = datetime.utcnow() + timedelta(hours=24)
        payload['exp'] = expiration_date
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token
    except Exception as e:
        return e


def validate_token(secret_key):
    try:
        token = request.headers.get('authorization')
        if token:
            refined_token = refine_token(token)
            decoded_token = jwt.decode(refined_token, secret_key)
            return decoded_token
        else:
            raise CustomException('Token must be provided!', status=401)
    except jwt.exceptions.DecodeError:
        e = CustomException('Invalid token', status=401)
        return e.get_exception_obj()
    except jwt.exceptions.ExpiredSignatureError:
        e = CustomException(
            'Your token have expired please login again', status=401)
        return e.get_exception_obj()
    except (CustomException) as e:
        return e.get_exception_obj()
    except Exception as e:
        return e


def authenticate(secret_key):
    try:
        decoded_token = validate_token(secret_key)
        if 'message' and 'status' in decoded_token:
            raise CustomException(
                decoded_token['message'], decoded_token['status'])
        else:
            email = decoded_token['email']
            id = decoded_token['id']

            confirmed_user = User.check_user_id(email, id)
            if confirmed_user:
                return confirmed_user
            else:
                message = 'User authentication failed.'
                raise CustomException(message, status=401)

    except CustomException as e:
        return e.get_exception_obj()
    except Exception as e:
        return e
