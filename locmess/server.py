"""
HTTP server that handles the request from the client application.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from .locmess import LocMess
from .exceptions import UserAlreadyExistsError
import json

NEW_USER = '/new/user'
LOGIN = '/login'
LOGOUT = '/logout'

lm = LocMess()

# HTTPRequestHandler class
class Server(BaseHTTPRequestHandler):

    # GET
    def do_GET(self):
        print(self.path)
        print(self.headers['content'])
        path = self.path
        json_content = self.headers['content']

        json_dict = json.loads(json_content)
        print('Loaded json: ')
        print(json_dict)

        if LOGIN in path:
            login(json_dict)

        return

    def do_POST(self):
        print(self.path)
        print(self.headers['content'])
        path = self.path
        json_content = self.rfile.read(int(self.headers['Content-Length']))

        print('Raw Content')
        print(json_content)

        json_dict = json.loads(json_content)
        print('Loaded json: ')
        print(json_dict)

        if LOGIN in path:
            self.login(json_dict)
        if NEW_USER in path:
            self.add_user(json_dict)
        if LOGOUT in path:
            self.logout(json_dict)

        return


    # TODO: refactor those to a new class
    def login(self, args):
        token = lm.login(args['username'], args['password'])

        if token is None:
                self.send_response(401)
                self.send_header('Content-type','text/html')
                self.end_headers()
                return

        ret_json = {'token':token.decode()}
        ret_json = json.dumps(ret_json)

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        self.wfile.write(ret_json.encode())
        return

    def add_user(self, args):
        try:
            lm.add_user(args['username'], args['password'])
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
        except Exception as e:
            self.send_response(401)
            self.send_header('Content-type','text/html')
            self.end_headers()
            ret_json = {'error':str(e)}
            ret_json = json.dumps(ret_json)
            self.wfile.write(ret_json.encode())

    def logout(self, args):
        try:
            lm.logout(args['username'], args['token'].encode())
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
        except Exception as e:
            self.send_response(401)
            self.send_header('Content-type','text/html')
            self.end_headers()
            ret_json = {'error':str(e)}
            ret_json = json.dumps(ret_json)
            self.wfile.write(ret_json.encode())
