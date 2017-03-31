"""
Contains the interface for interaction with the server-side app. This includes
the directives to interact with the database, user managment, etc.
"""
from pony.orm import *
from locmess import settings
from locmess.tables import User
import hashlib
from cryptography.fernet import Fernet
from locmess.decorators import authentication_required

from base64 import b64encode, b64decode
from locmess.exceptions import UserAlreadyExistsError

class LocMess(object):

    def __init__(self):
        pass

    @db_session
    def add_user(self, username, password):
        pwd_hash = self._get_password_hash(username, password)
        if (User.get(username=username) is not None):
            raise UserAlreadyExistsError('Username \'{}\' '
                                         'already exists'.format(username))
        User(username=username, password=pwd_hash)

    @db_session
    def login(self, username, password):
        res = User.get(username=username,
                       password=self._get_password_hash(username, password))
        if res is None:
            return None  # login failed
        token = self._generate_token(username)
        self._update_user_token(username, token)
        return token

    @db_session
    def get_user(self, username):
        """
        Returns the User object with the provided username.

        This is not a login function: it does not do any checks regarding the
        password.
        """
        return User.get(username=username)

    @db_session
    @authentication_required
    def logout(self, username, token):
        """
        Removes the session associated with the user.
        """
        # NOTE: exception messages are useful for clients
        u = self.get_user(username)
        u.token = None

    def _get_password_hash(self, str_user, str_pwd):
        digest = hashlib.pbkdf2_hmac('sha256', str_pwd.encode(),
                                     str_user.encode(),
                                     settings.PBKDF2_ITERATIONS)
        return b64encode(digest).decode()

    def _generate_token(self, username):
        """
        Generates a new token.

        Token format: {username}Ks
        """
        key = self._get_key()
        fernet = Fernet(key)
        token = fernet.encrypt(username.encode())
        return token

    def _is_token_valid(self, username, token):
        fernet = Fernet(key)
        dec_token = fernet.decrypt(token)
        return dec_token == username

    def _get_key(self):
        key = None
        with open(settings.KEY_PATH, 'rb') as f:
            key = f.read()
        return key

    @db_session
    def _update_user_token(self, username, token):
        """
        Update user token.

        "token" must be a base64 encoded token.
        """
        u = User.get(username=username)
        u.token = token
