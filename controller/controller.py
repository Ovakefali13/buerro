from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
import sqlite3
import re
import json

from chatbot import Chatbot, Intent
from . import NotificationHandler
from usecase import Usecase, Reply
from services.singleton import Singleton

@Singleton
class UsecaseStore:
    def __init__(self):
        # TODO Multi-User: by User
        self.usecase_instances = {}

    def get(self, UsecaseCls):
        if UsecaseCls not in self.usecase_instances:
            self.usecase_instances[UsecaseCls] = UsecaseCls()
        return self.usecase_instances[UsecaseCls]

def ControllerFromArgs(chatbot:Chatbot, usecase_by_context:dict):
    class CustomController(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.notification_handler = NotificationHandler.instance()
            self.chatbot = chatbot
            self.usecase_by_context = usecase_by_context
            for usecase in usecase_by_context.values():
                if not issubclass(usecase, Usecase):
                    raise Exception(f'Usecase {usecase} is not a sub-class of '
                        +'Usecase')

            super(CustomController, self).__init__(*args, **kwargs)

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

            def respond_text(http_code:int, msg:str):
                self.send_response(http_code)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(msg.encode("utf-8"))

            def respond_json(http_code:int, body:dict):
                self.send_response(http_code)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(body).encode('utf-8'))

            def respond_error(id:str, message:str):
                answer = {
                    'error': {
                        'id': id,
                        'message': message
                    }
                }
                respond_json(500, answer)

            def parse_body():
                length = int(self.headers['Content-Length'])
                payload = self.rfile.read(length).decode('utf-8')
                return json.loads(payload)

            body = parse_body()

            if self.path == "/message":

                msg = body.get('message', '')
                if msg == 'ping':
                    respond_text(200, 'pong')
                elif msg == 'shutdown':
                    respond_text(200, 'shutdown')
                else:
                    intent = self.chatbot.get_intent(msg)
                    UsecaseCls = self.usecase_by_context.get(intent.context, None)
                    if not UsecaseCls:
                        respond_text(500, f'no usecase detected for intent {intent}')
                    else:
                        usecase = UsecaseStore.instance().get(UsecaseCls)

                        reply = usecase.advance(intent.message)
                        if not isinstance(reply, Reply):
                            respond_text(500, 'usecase advance does not Reply')
                            raise Exception(f"Usecase {usecase}'s advance does"
                                            +" not return a Reply object")
                        respond_json(200, reply)

                del msg

            if self.path == "/save-subscription":
                print('/save-subscription ...')
                try:
                    self.notification_handler.save_subscription(body)
                    respond_json(200, { 'data': { 'success': True }})
                except Exception as e:
                    print(e)
                    self.respond_error('unable-to-save-subscription',
                        'The subscription was received but we were unable to'
                        + 'save it to our database.')

    return CustomController

