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
                    valid_from=None, valid_until=None, properties=None):
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
            valid_until=valid_until, properties=properties)

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
    @authentication_required
    def get_location_by_name(self, username, token, name):
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
        msgs = self._filter_messages_by_properties(msgs, username, token)
        return msgs

    @db_session
    @authentication_required
    def get_available_messages_by_ssid(self, username, token, my_ssids):
        logging.debug('Request for available messages by SSID list')
        logging.debug('\t My SSID List: {}'.format(my_ssids))
        msgs = self._get_messages_in_ssid_range(my_ssids)
        msgs = self._filter_messages_by_properties(msgs, username, token)
        return msgs

    @db_session
    def _get_messages_in_ssid_range(self, my_ssids):
        ssid_msgs = select(m for m in Message
                             if not m.location.is_gps)
        ssid_msgs_in_range = self._filter_ssid_msgs_in_range(ssid_msgs, my_ssids)
        return ssid_msgs_in_range

    def _filter_ssid_msgs_in_range(self, ssid_msgs, my_ssids):
            res = [msg for msg in ssid_msgs
                       if self._is_in_range_from_ssid_list(msg.location.location,
                                                            my_ssids)
                  ]
            res_without_duplicates = set(res)
            return res_without_duplicates

    @db_session
    def _get_messages_in_range(self, curr_coord):
        gps_msgs = select(m for m in Message
                            if m.location.is_gps)
        gps_msgs_in_range = self._filter_msgs_in_range(gps_msgs, curr_coord)
        return gps_msgs_in_range

    @db_session
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
        # support both: passing location as a json string or as a json obj
        if isinstance(location_json, dict):
            location = location_json
        else:
            location = json.loads(location_json)

        latitude = location['latitude']
        longitude = location['longitude']
        radius = location['radius']

        return ((latitude, longitude), radius)

    def _is_in_range_from_ssid_list(self, ssid_list, my_ssids):
        ssid_list = self._parse_ssid_location_from_json(ssid_list)
        for ssid in my_ssids:
            if ssid in ssid_list:
                logging.debug('\t* {} is in {}'.format(ssid, ssid_list))
                return True
            logging.debug('\t* {} is not in list {}'.format(ssid, ssid_list))
        return False

    def _parse_ssid_location_from_json(self, location_json):
        # support both: passing location as a json string or as a json obj
        if isinstance(location_json, dict):
            ssid_location = location_json
        else:
            ssid_location = json.loads(location_json)

        ssid_list = ssid_location['ssids']
        return ssid_list

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

    ### Profile Related ###

    @db_session
    @authentication_required
    def update_key(self, username, token, key, value):
        """
        Updates or adds (if does not exist) the key-value pair to the user's
        profile.

        To remove a key, simply update it with the None value.
        """
        logging.debug('### update_key() ###')
        u = User.get(username=username)
        kvp = u.kvp

        if kvp is None:
            logging.warning('\tKVP for user "{}" is None, instantiating'.format(username))
            kvp = {}
        else:
            kvp = json.loads(kvp)

        logging.debug('\tAssociating {}:{} for user {}'.format(key, value, username))
        kvp[key] = value
        u.kvp = json.dumps(kvp)

    @db_session
    @authentication_required
    def delete_key(self, username, token, key):
        """
        Deltes the key-value pair with the provided key from the user's
        profile. If a pair with that key does not exist, it's ignored.
        """
        logging.debug('### delete_key() ###')
        u = User.get(username=username)
        kvp = u.kvp

        if kvp is None:
            logging.warning('\tKVP is None for user {}'.format(username))
            return
        else:
            kvp = json.loads(kvp)

        try:
            logging.debug('\tDeleting key {} for user {}'.format(key, username))
            del kvp[key]
            u.kvp = json.dumps(kvp)
        except KeyError:
            # all good: deleting a non-existing key, just ignore
            logging.debug('\t\t[!!] Key {} was non-existent'.format(key))
            pass

    @db_session
    @authentication_required
    def get_value(self, username, token, key):
        """
        Returns the value indexed by the specified key. If there is no entry
        indexed by that key, None is returned.
        """
        logging.debug('### get_value() ###')
        u = User.get(username=username)
        kvp = u.kvp

        if kvp is None:
            logging.warning('\tKVP is None for user {}'.format(username))
            return None
        else:
            kvp = json.loads(kvp)

        try:
            logging.debug('\tGetting value for key {} for user {}'.format(key, username))
            value = kvp[key]
            logging.debug('\t\tValue for key {} is {}'.format(key, value))
            return value
        except KeyError:
            # key-value entry does not exist, return None
            logging.warning('\t\t[!!]Key {} not found'.format(key))
            return None

    @db_session
    @authentication_required
    def get_key_value_bin(self, username, token):
        """
        Returns the key-value dictionary for this user.
        """
        logging.debug('### get_key_value_bin ###')
        u = User.get(username=username)
        kvp = u.kvp

        if kvp is None:
            logging.warning('\tKVP is None for user {}'.format(username))
            return {}
        else:
            kvp = json.loads(kvp)

        return kvp

    @db_session
    def _filter_messages_by_properties(self, msgs, username, token):
        res = []
        u = User.get(username=username)
        for msg in msgs:
            msg_props = json.loads(msg.properties)

            if msg_props == {}:
                res += [msg]
                continue

            u_kvp = self.get_key_value_bin(username, token)
            if msg.is_black_list:
                # profiles that match DON'T receive messages
                # blacklist policy
                if not msg_props == u_kvp:
                    res += [msg]
            else:
                # whitelist polict
                # ONLY profiles that MATCH receive the messages
                if msg_props == u_kvp:
                    res += [msg]
        return res
