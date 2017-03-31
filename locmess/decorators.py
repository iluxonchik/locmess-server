from functools import wraps
from pony.orm import *
from locmess.tables import User
from locmess.exceptions import UserNotFoundError, TokenInvalidError
def authentication_required(f):
    """
    Makes sure that the user is correctly authenticated.

    This decorator expectes that the first argument is "username" and second
    is "token".
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # handle case if first argument is "self"
        start_index = 0 if isinstance(args[0], str) else 1

        username = args[start_index]
        token = args[start_index + 1]

        u = User.get(username=username)

        # NOTE: aware of information leakage if exception messages are returned
        # to the client unchanged
        if u is None:
            raise UserNotFoundError('User "{}"" not found.'.format(username))

        if u.token != token:
            raise TokenInvalidError('Token "{}" is invalid for user "{}".'.format(token, username))

        return f(*args, **kwargs)
    return decorated_function