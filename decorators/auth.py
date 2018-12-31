from functools import wraps
from ..helpers.user_helpers import authenticate
from ..settings import SECRET_KEY

secret_key = SECRET_KEY


def auth_user(f):
    @wraps(f)
    def decorated_auth():
        f(secret_key)
    return decorated_auth
