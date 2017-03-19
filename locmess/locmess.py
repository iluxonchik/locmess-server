"""
Contains the interface for interaction with the server-side app. This includes
the directives to interact with the database, user managment, etc.
"""
from pony.orm import *
from locmess import settings
from locmess.tables import User, Token
import hashlib
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
                       password=self._get_password_hash(password))
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

    def _get_password_hash(self, str_user, str_pwd):
        digest = hashlib.pbkdf2_hmac('sha256', str_pwd.encode(),
                                     str_user.encode(),
                                     settings.PBKDF2_ITERATIONS)
        return b64encode(digest).decode()
