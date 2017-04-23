"""
HTTP server that handles the request from the client application.
"""
from locmess.decorators import handle_expcetions
from http.server import BaseHTTPRequestHandler, HTTPServer
from .locmess import LocMess
from .exceptions import UserAlreadyExistsError
import json
from locmess.settings import logging
from pony.orm import *
import dateutil.parser


# User related
NEW_USER = '/new/user'  # {username, password}
LOGIN = '/login'  # {username, password}
LOGOUT = '/logout' # {username, token}

# Location related
NEW_LOCATION =  '/new/location'  # {username, token, name, is_gps, location_json }
GET_LOCATION = '/get/location'   # {username, token, name}
GET_ALL_LOCATIONS = '/get/location/all' # {username, token, name}

# Message realted
NEW_MESSAGE = '/new/message'  # {username, token, title, location_name, text, is_centralized, is_black_list, properties, valid_from?, valid_until?}
GET_GPS_MESSAGES = '/get/message/gps' # {username, token, curr_coord}
GET_SSID_MESSAGES = '/get/message/ssid'
DELETE_MESSAGE = '/delete/message' # {username, token, msg_id}
GET_MY_MESSAGES = '/get/message/my' # {username, token}

# Profile related
UPDATE_KEY = '/profile/key/update' # {username, token, key, value}
DELETE_KEY = '/profile/key/delete' # {username, token, key, value}
GET_KEY_VALUE_BIN = '/get/profile/keys' # {username, token}

lm = LocMess()

# HTTPRequestHandler class
class Server(BaseHTTPRequestHandler):


    def __init__(self, *args, **kwargs):
        # NOTE: do all of the setup and then call the super's __init__.
        # After digging into the source code, I found out that BaseRequestHandler
        # (parent of BaseHTTPRequestHandler) calls handle() in its constructor,
        # so that means that the overriden do_* methods will be called straight
        # away, beofore running any other code in Server's __init__.
        # https://github.com/python/cpython/blob/master/Lib/socketserver.py#L695
        self.RES_FUNC = {
            LOGIN: self.login,
            NEW_USER: self.add_user,
            LOGOUT: self.logout,
            NEW_LOCATION: self.add_location,
            GET_ALL_LOCATIONS: self.get_all_locations,
            GET_LOCATION: self.get_location,
            NEW_MESSAGE: self.add_message,
            GET_GPS_MESSAGES: self.get_gps_messages,
            GET_SSID_MESSAGES: self.get_ssid_messsages,
            UPDATE_KEY: self.update_profile_key,
            DELETE_KEY: self.delete_profile_key,
            GET_KEY_VALUE_BIN: self.get_key_value_bin,
            DELETE_MESSAGE: self.delete_message,
            GET_MY_MESSAGES: self.get_my_messages,
        }
        super(Server, self).__init__(*args, **kwargs)

    def do_GET(self):
        logging.debug(self.path)
        logging.debug(self.headers['content'])
        path = self.path
        json_content = self.headers['content']

        json_dict = json.loads(json_content)
        logging.debug('Loaded json: ')
        logging.debug(json_dict)

    def do_POST(self):
        logging.debug(self.path)
        logging.debug(self.headers['content'])
        path = self.path
        json_content = self.rfile.read(int(self.headers['Content-Length']))

        logging.debug('Raw Content')
        logging.debug(json_content)

        json_dict = json.loads(json_content)
        logging.debug('Loaded json: ')
        logging.debug(json_dict)

        dispatch_function = self.RES_FUNC.get(self.path, self.invalid_endpoint_err)
        dispatch_function(json_dict)

    @handle_expcetions
    def login(self, args):
        token = lm.login(args['username'], args['password'])

        if token is None:
                self.send_response(401)
                self.send_header('Content-type','text/html')
                self.end_headers()
                return

        ret_json = {'token':token.decode()}
        self._send_OK_headers()
        self._respond_json(ret_json)


    def invalid_endpoint_err(self, args):
        self._send_UNAUTH_headers('\'{}\' is an invalid endpoint.'.format(self.path))

    @handle_expcetions
    def add_user(self, args):
        lm.add_user(args['username'], args['password'])
        self._send_OK_headers()

    @handle_expcetions
    def logout(self, args):
        lm.logout(args['username'], args['token'].encode())
        self._send_OK_headers()

    @handle_expcetions
    def add_location(self, args):
        # {username, token, name, is_gps, location_json }
        username, token = self._parse_auth(args)
        name, is_gps, location_json = args['name'], args['is_gps'], args['location_json']
        lm.add_location(username, token, name, is_gps, location_json)
        self._send_OK_headers()

    @db_session
    @handle_expcetions
    def get_all_locations(self, args):
        # { username, token }
        logging.info('# get_location #')
        username, token = self._parse_auth(args)

        locations = lm.get_all_locations(username, token)
        res_list = [self._locations_to_json_dict(loc) for loc in locations]

        self._respond_json(res_list)

    @db_session
    @handle_expcetions
    def get_location(self, args):
        # { username, token, name }
        logging.info('# get_location #')
        username, token = self._parse_auth(args)
        name = args['name']
        location = lm.get_location_by_name(username, token, name)
        res_dict = {
                        'name': location.name,
                        'author': location.author.username,
                        'is_gps': location.is_gps,
                        'location': location.location,
                   }
        logging.info('\t* replying with dict:')
        logging.info('\t\t{}'.format(res_dict))

        self._respond_json(res_dict)

    @db_session
    @handle_expcetions
    def add_message(self, args):
         # {
         #    username, token, title, location_name, text, is_centralized,
         #    is_black_list, properties, valid_from?, valid_until?
         # }
         username, token = self._parse_auth(args)
         title = args['title']
         location_name = args['location_name']
         location = None
         with db_session:
             location = lm.get_location_by_name(username, token, location_name)
         text = args['text']
         is_centralized = args['is_centralized']
         is_black_list = args['is_black_list']
         properties = args['properties']

         valid_from = None
         try:
             valid_from = args['valid_from']
             valid_from = dateutil.parser.parse(valid_from)
         except KeyError as e:
             pass

         valid_until = None
         try:
             valid_until = args['valid_until']
             valid_until = dateutil.parser.parse(valid_until)
         except KeyError as e:
             pass

         lm.add_message(username, token,
         title=title, location=location,
         text=text, is_centralized=is_centralized, is_black_list=is_black_list,
         valid_from=valid_from, valid_until=valid_until, properties=properties)

         self._send_OK_headers()


    @handle_expcetions
    def get_gps_messages(self, args):
        # { username, token, curr_coord }

        username, token = self._parse_auth(args)
        curr_coord = args['curr_coord']

        msgs = lm.get_available_messages_by_gps(username, token, curr_coord)
        json_msgs = [json.dumps(self._msg_to_json_dict(msg)) for msg in msgs]
        msgs_dict = {
                        'messages': json_msgs
                    }
        self._respond_json(msgs_dict)

    @handle_expcetions
    def get_ssid_messsages(self, args):
        # {username, token, my_ssids}
        logging.debug('### get_ssid_messsages() ###')
        username, token = self._parse_auth(args)
        my_ssids = args['my_ssids']
        msgs = lm.get_available_messages_by_ssid(username, token, my_ssids)
        json_msgs = [json.dumps(self._msg_to_json_dict(msg)) for msg in msgs]
        msgs_dict = {
                        'messages': json_msgs,
                    }
        self._respond_json(msgs_dict)

    @handle_expcetions
    def delete_message(self, args):
        username, token = self._parse_auth(args)
        msg_id = args['msg_id']
        lm.delete_message(username, token, msg_id)
        self._send_OK_headers()

    @handle_expcetions
    def get_my_messages(self, args):
        username, token = self._parse_auth(args)
        msg_list = lm.get_my_messages(username, token)
        res = [self._msg_to_json_dict(msg) for msg in msg_list]
        self._respond_json(res)

    @handle_expcetions
    def update_profile_key(self, args):
        username, token = self._parse_auth(args)
        key = args['key']
        value = args['value']
        lm.update_key(username, token, key, value)
        self._send_OK_headers()

    @handle_expcetions
    def delete_profile_key(self, args):
        username, token = self._parse_auth(args)
        key = args['key']
        lm.delete_key(username, token, key)
        self._send_OK_headers()

    @handle_expcetions
    def get_key_value_bin(self, args):
        username, token = self._parse_auth(args)
        res = lm.get_key_value_bin(username, token)
        self._respond_json(res)

    def _locations_to_json_dict(self, loc_obj):
        res_dict = {
                        'name':   loc_obj.name,
                        'author': loc_obj.author.username,
                        'is_gps': loc_obj.is_gps,
                        'location': loc_obj.location,
        }
        return res_dict

    def _msg_to_json_dict(self, msg_obj):
        msg_dict = {    'msg_id': msg_obj.id,
                        'author': msg_obj.author.username,
                        'title': msg_obj.title,
                        'location': msg_obj.location.location,
                        'text': msg_obj.text,
                        'is_centralized': msg_obj.is_centralized,
                        'is_black_list': msg_obj.is_black_list,
                        'valid_from': msg_obj.valid_from.isoformat(),
                        'valid_until': msg_obj.valid_until.isoformat(),
                        'time_posted': msg_obj.time_posted.isoformat(),
                        'properties': msg_obj.properties,
                   }
        return msg_dict

    def _respond_json(self, json_dict):
        self._send_OK_headers()
        res = json.dumps(json_dict)
        self.wfile.write(res.encode())

    def _send_OK_headers(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()

    def _send_UNAUTH_headers(self, msg=None):
        self.send_response(401)
        self.send_header('Content-type','application/json')
        self.end_headers()

        if msg:
            ret_json = {'error': msg}
            ret_json = json.dumps(ret_json)
            self.wfile.write(ret_json.encode())

    def _parse_auth(self, args):
        return (args['username'], args['token'].encode())
