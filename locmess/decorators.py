import json, sys, traceback
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
        use_kwargs = False
        username = None
        try:
            username = args[start_index]
        except IndexError as e:
            # username being passed as kwargs
            username=kwargs['username']
            use_kwargs = True

        token = None
        if use_kwargs:
            token = kwargs['token']
        else:
            try:
                token = args[start_index + 1]
            except IndexError as e:
                token = kwargs['token']

        u = User.get(username=username)

        # NOTE: aware of information leakage if exception messages are returned
        # to the client unchanged
        if u is None:
            raise UserNotFoundError('User "{}" not found.'.format(username))

        if u.token != token:
            raise TokenInvalidError('Token "{}" is invalid for user "{}".'.format(token, username))

        return f(*args, **kwargs)
    return decorated_function

def handle_expcetions(f):
    """
    Handles any excepitons and returns the error message, as well as a 401
    response code back to the client. If everything goes well, headers are
    set to the "OK" state (201 response code).

    IMPORTANT: must only be used within BaseHTTPRequestHandler.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        handler = args[0]  # self

        try:
            f(*args, **kwargs)
        except Exception as e:
            handler.send_response(401)
            handler.send_header('Content-type','application/json')
            handler.end_headers()

            ret_json = {'error': str(e)}
            ret_json = json.dumps(ret_json)
            handler.wfile.write(ret_json.encode())

            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, file=sys.stdout)

    return decorated_function
