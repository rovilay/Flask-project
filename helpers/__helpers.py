from flask import Response, json
import bcrypt
import re
# from .user_helpers import refine_token


def refine_token(token):
    try:
        reg = re.compile(r"(^(b'))")
        refined_token = token if reg.match(
            token) is None else token.split("'")[1]
        return refined_token
    except Exception as e:
        return e


def server_res(message, success=False, status=500, location='/books', book_data=None, **kwargs):
    args_copy = locals().copy()

    if 'kwargs' in args_copy:
        args_copy.update(args_copy['kwargs'])
        del args_copy['kwargs']

    del args_copy['location']

    res_body = {key: value for key, value in args_copy.items()
                if value is not None}

    response = Response(
        json.dumps(res_body), status=status, mimetype='application/json')
    response.headers['Location'] = location
    return response


def hash_password(password):
    byte_password = bytes(password, encoding='utf-8')
    hashed = bcrypt.hashpw(byte_password, bcrypt.gensalt())
    hash_refined = refine_token(str(hashed))

    return hash_refined


def check_password(password, hashed):
    byte_password = bytes(password, encoding='utf-8')
    hasheds = '$2y$12$sZvqknq.WcatWo/dr4eJt.WB1fSmOi1ot7gYbzCX5lPXlFEUWmKSu'
    check = bcrypt.checkpw(byte_password, bytes(hashed, encoding='utf-8'))
    return check


class CustomException(Exception):
    def __init__(self, message, status=500):
        super().__init__(self, message)
        self.message = message
        self.status = int(status)

    def get_exception_obj(self):
        return {'message': self.message, 'status': self.status}
