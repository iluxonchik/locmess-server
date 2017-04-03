"""
Contains the interface for interaction with the server-side app. This includes
the directives to interact with the database, user managment, etc.
"""
from pony.orm import *
from locmess import settings
from locmess.settings import logging
from locmess.tables import User, Message, Location
import hashlib
import json
from cryptography.fernet import Fernet
from locmess.decorators import authentication_required
from haversine import haversine
from datetime import datetime

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

    @authentication_required
    def add_message(self, username, token, title, location, text,
                    is_centralized=True, is_black_list=True,
                    valid_from=None, valid_until=None,
                    is_visible=True, properties=None):
        """
        Adds a new message.
        """
        if valid_from is None:
            valid_from = datetime.now
        if valid_until is None:
            valid_until = datetime.max
        if properties is None:
            properties = json.dumps({})

        author = None
        with db_session:
            author = self.get_user(username=username)

        logging.debug('Adding message "{}" for user {}'.format(title, author))

        msg = None
        with db_session:
            msg = Message(author=author, title=title, location=location,
            text=text,
            is_centralized=is_centralized, is_black_list=is_black_list,
            valid_until=valid_until, properties=properties,
            is_visible=is_visible)

        return msg

    @db_session
    @authentication_required
    def add_location(self, username, token, name, is_gps, location_json):
        author = self.get_user(username)
        logging.debug('Adding location "{}" is_gps: {},'
                      'author: {}'.format(name, is_gps, author))
        loc = Location(author=author, name=name, is_gps=is_gps, location=location_json)
        return loc

    @db_session
    def get_location_by_name(self, name):
        logging.debug('Getting location "{}" by name'.format(name))
        return Location.get(name=name)

    @db_session
    @authentication_required
    def get_available_messages_by_gps(self, username, token, curr_coord):
        """
        Gets a list of available messages for the user in the provided
        location.

        Args:
            curr_coord - tuple of (latitude, longitude) of the current
            user's location.
        """
        logging.debug('Request for available messages by GPS corrdinates')
        msgs = self._get_messages_in_range(curr_coord)
        return msgs

    @db_session
    def _get_messages_in_range(self, curr_coord):
        gps_msgs = select(m for m in Message
                            if m.location.is_gps)
        gps_msgs_in_range = self._filter_msgs_in_range(gps_msgs, curr_coord)
        return gps_msgs_in_range


    def _filter_msgs_in_range(self, msgs, curr_coord):
        res = [msg for msg in msgs
                   if self._is_in_range_from_json_coord(
                                    msg.location.location, curr_coord)
              ]
        return res

    def _is_in_range_from_json_coord(self, json_coord, curr_coord):
        loc_coord, radius = self._parse_location_from_json(json_coord)
        logging.debug('Parsed location: '
                      'latitude={}, longitude={}, radius={}'.format(
                                    loc_coord[0], loc_coord[1], radius))
        return self._is_in_range(loc_coord, curr_coord, radius)


    def _parse_location_from_json(self, location_json):
        location = json.loads(location_json)
        latitude = location['latitude']
        longitude = location['longitude']
        radius = location['radius']

        return ((latitude, longitude), radius)

    def _is_in_range(self, ref_coord, my_coord, radius):
        return self._get_distance_in_between_coordinates_in_meters(ref_coord, my_coord) <= radius

    def _get_distance_in_between_coordinates_in_meters(self, coord1, coord2):
        return haversine(coord1, coord2) * 1000

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
