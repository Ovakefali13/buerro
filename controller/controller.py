from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
import sqlite3
import re
import json

from chatbot import Chatbot
from . import NotificationHandler, LocationHandler

def ControllerFromArgs(chatbot:Chatbot, usecaseByContext:dict):
    class CustomController(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.notification_handler = NotificationHandler.instance()
            self.location_handler = LocationHandler.instance()
            self.chatbot = chatbot
            self.usecaseByContext = usecaseByContext
            super(CustomController, self).__init__(*args, **kwargs)

            self.last_location = None

        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-type, Authorization')
            BaseHTTPRequestHandler.end_headers(self)

        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_POST(self):

            def respond_json(http_code:int, body:dict):
                self.send_response(http_code)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(body).encode('utf-8'))

            def respond_succ(message=None):
                answer = {
                    'success': True,
                }
                if type(message) == str:
                    answer = {
                        **answer,
                        'message': message
                    }
                elif type(message) == dict:
                    answer = {
                        **answer,
                        **message
                    }
                respond_json(200, answer)

            def respond_error(http_code, message:str):
                answer = {
                    'error': {
                        'message': message
                    }
                }
                respond_json(http_code, answer)

            def parse_body():
                length = int(self.headers['Content-Length'])
                payload = self.rfile.read(length).decode('utf-8')
                return json.loads(payload)

            body = parse_body()

            if self.path == "/message":

                if 'location' in body and len(body['location']) == 2:
                    lat, lon = tuple(body['location'])
                    self.location_handler.set(lat, lon)

                msg = body.get('message', '')

                if msg == 'shutdown':
                    respond_succ('shutdown')
                else:
                    intent = self.chatbot.get_intent(msg)
                    usecase = self.usecaseByContext.get(intent, None)
                    if usecase:
                        usecase = usecase.instance()
                        reply = usecase.advance(msg)
                        respond_succ(reply)
                    else:
                        respond_text(500, 'no usecase detected')

                del msg

            elif self.path == "/save-subscription":
                print('/save-subscription ...')
                try:
                    self.notification_handler.save_subscription(body)
                    respond_succ()
                except Exception as e:
                    print(e)
                    respond_error(500,
                        'The subscription was received but we were unable to'
                        + 'save it to our database.')

            elif self.path == "/location":
                if 'location' in body and len(body['location']) == 2:
                    lat, lon = tuple(body['location'])
                    self.location_handler.set(lat, lon)
                    respond_succ()
                else:
                    respond_error(400, 'bad location request')
            else:
                respond_error(404, 'Not Found')

    return CustomController

