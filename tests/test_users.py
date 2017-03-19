"""
Class containing tests for User creation, login, logout, as well as token
managment.
"""

# IMPORTANT: dirty hack to make the tests use a separate testing database.
# Those two lines should be the first ones in every test file
from locmess import settings
setattr(settings, 'DB_FILE_NAME', settings.TEST_DB_FILE_NAME)

import os
import requests
import unittest
from pony.orm import *

from locmess.locmess import LocMess
from locmess.exceptions import UserAlreadyExistsError

import locmess.tables as tables
from locmess.tables import User, Token

class UserManagmentTestCase(unittest.TestCase):

    U1_USR = 'thegame'
    U1_PWD = 'the documentary'

    def setUp(self):
        self._lm = LocMess()

    def tearDown(self):
        os.remove(settings.TEST_PATH + settings.TEST_DB_NAME)

    @db_session
    def test_new_user_registration(self):
        self._lm.add_user(self.U1_USR, self.U1_PWD)
        expected_u1 = User.get(username=self.U1_USR)
        u1 = self._lm.get_user(self.U1_USR)
        self.assertEqual(u1, expected_u1, 'Invalid username obtained.')

    def test_duplicate_user_not_created(self):
        self._lm.add_user(self.U1_USR, self.U1_PWD)
        with self.assertRaises(UserAlreadyExistsError):
            self._lm.add_user(self.U1_USR, self.U1_PWD)

    def test_user_login_success(self):
        self._lm.add_user(self.U1_USR, self.U1_PWD)
        token = self._lm.login(self.U1_USR, self.U1_PWD)
        self.assertIsNotNone(token, 'Returned token is None (login failed)')

    def test_user_login_failure(self):
        WRONG_PWD = 'if you ever knew dre, you would say I was The New Dre'
        self._lm.add_user(self.U1_USR, self.U1_PWD)
        token = self._lm.login(self.U1_USR, WRONG_PWD)
        self.assertIsNone(token, 'Returned token is not None (login success)')


    def test_user_logout(self):
        pass

    def test_new_token_created(self):
        pass

    def test_user_auth_with_token(self):
        pass

    def test_user_auth_fail_with_wrong_token(self):
        pass
