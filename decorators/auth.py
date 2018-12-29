from functools import wraps
from ..helpers.user_helpers import authenticate
from ..settings import app

secret_key = app.config['SECRET_KEY']


def auth_user(f):
    @wraps(f)
    def decorated_auth():
        print('I am here')
        f(secret_key)
        print('after')
    return decorated_auth
