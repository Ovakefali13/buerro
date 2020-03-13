from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
import sqlite3
import re
import json

from chatbot import Chatbot, Intent
from . import NotificationHandler

def ControllerFromArgs(chatbot:Chatbot, usecaseByContext:dict):
    class CustomController(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.chatbot = chatbot
            self.usecaseByContext = usecaseByContext
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
                    usecase = self.usecaseByContext.get(intent.context, None)
                    if usecase:
                        usecase = usecase.instance()
                        reply = usecase.advance(intent.entities)

                        respond_json(200, reply)
                    else:
                        respond_text(500, 'no usecase detected')

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

