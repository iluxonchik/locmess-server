"""
Class containing tests for User creation, login, logout, as well as token
managment.
"""

# IMPORTANT: dirty hack to make the tests use a separate testing database.
# Those two lines should be the first ones in every test file
from locmess import settings

import os
import requests
import unittest
from pony.orm import *

from locmess.locmess import LocMess
from locmess.exceptions import (UserAlreadyExistsError, UserNotFoundError,
                                TokenInvalidError)

import locmess.tables as tables
from locmess.tables import User, db


class UserManagmentTestCase(unittest.TestCase):

    U1_USR = 'thegame'
    U1_PWD = 'the documentary'

    def setUp(self):
        self._lm = LocMess()
        db.create_tables()

    def tearDown(self):
        db.drop_all_tables(with_all_data=True)

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
        self.assertIsNotNone(token, 'Returned token is None (login failed).')

    def test_user_login_failure(self):
        WRONG_PWD = 'if you ever knew dre, you would say I was The New Dre'
        self._lm.add_user(self.U1_USR, self.U1_PWD)
        token = self._lm.login(self.U1_USR, WRONG_PWD)
        self.assertIsNone(token, 'Returned token is not None (login success)')

    @db_session
    def test_user_logout(self):
        """
        Make sure that the token (i.e. the session id is destroyed on logout).
        """
        self._lm.add_user(self.U1_USR, self.U1_PWD)
        user = User.get(username=self.U1_USR)
        token = user.token
        self.assertIsNone(token, 'Newly created user already has a token')

        token = self._lm.login(self.U1_USR, self.U1_PWD)
        user = User.get(username=self.U1_USR)
        token = user.token
        self.assertIsNotNone(token)

        # now, let's logout
        self._lm.logout(self.U1_USR, token)
        user = User.get(username=self.U1_USR)
        token = user.token
        self.assertIsNone(token, 'Token not removed on logout.')

    @db_session
    def test_new_token_created(self):
        self._lm.add_user(self.U1_USR, self.U1_PWD)
        token = self._lm.login(self.U1_USR, self.U1_PWD)
        user = self._lm.get_user(self.U1_USR)
        saved_token = user.token
        self.assertEqual(token, saved_token)

        prev_token = token
        token = self._lm.login(self.U1_USR, self.U1_PWD)
        self.assertNotEqual(token, prev_token, 'Token was not re-generated'
                                               'on login.')

        saved_token = User.get(username=self.U1_USR).token
        self.assertEqual(token, saved_token, 'Token mismatch')

    def test_user_logout_fail_with_wrong_token(self):
        """
        Try performing a logout action with a wrong token and make sure that
        it's refused.
        """
        self._lm.add_user(self.U1_USR, self.U1_PWD)
        token = self._lm.login(self.U1_USR, self.U1_PWD)

        with self.assertRaises(TokenInvalidError):
            self._lm.logout(self.U1_USR, b'the chronic 1992')

    def test_user_logout_fail_with_non_exitent_user(self):
        """
        Try performing a logout action with non-existing user and make sure that
        it's refused.
        """
        self._lm.add_user(self.U1_USR, self.U1_PWD)
        token = self._lm.login(self.U1_USR, self.U1_PWD)

        with self.assertRaises(UserNotFoundError):
            self._lm.logout('Dr.Dre', token)
