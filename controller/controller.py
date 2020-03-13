from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
import sqlite3
import re
import json

from chatbot import Chatbot, Intent


def ControllerFromArgs(chatbot:Chatbot, usecaseByContext:dict):
    class CustomController(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.chatbot = chatbot
            self.usecaseByContext = usecaseByContext
            super(CustomController, self).__init__(*args, **kwargs)

        def save_subscription(self, subscription:dict):
            conn = sqlite3.connect('buerro.db')
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS subscription
                            (endpoint text, p256dh text, auth text)''')
            values = (subscription['endpoint'], subscription['keys']['p256dh'],
                subscription['keys']['auth'])
            c.execute('INSERT INTO subscription VALUES (?,?,?)', values)
            conn.commit()
            conn.close()

        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-type, Authorization')
            BaseHTTPRequestHandler.end_headers(self)

        def respond_text(self, http_code:int, msg:str):
            self.send_response(http_code)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(msg.encode("utf-8"))

        def respond_json(self, http_code:int, body:dict):
            self.send_response(http_code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(body).encode('utf-8'))

        def respond_error(self, id:str, message:str):
            answer = {
                'error': {
                    'id': id,
                    'message': message
                }
            }
            self.respond_json(500, answer)

        def do_OPTIONS(self):
            self.respond_text(200, 'options')
            self.end_headers()

        def do_POST(self):

            def parse_body():
                length = int(self.headers['Content-Length'])
                payload = self.rfile.read(length).decode('utf-8')
                return json.loads(payload)

            body = parse_body()

            if self.path == "/message":

                msg = body.get('message', '')[0]
                if msg == 'ping':
                    self.respond_text(200, 'pong')
                elif msg == 'shutdown':
                    self.respond_text(200, 'shutdown')
                else:
                    intent = self.chatbot.get_intent(msg)
                    usecase = self.usecaseByContext.get(intent.context, None)
                    if usecase:
                        usecase = usecase.instance()
                        reply = usecase.advance(intent.entities)

                        self.respond_text(200, reply)
                    else:
                        self.respond_text(500, 'no usecase detected')

                del msg

            if self.path == "/save-subscription":
                print('/save-subscription ...')
                try:
                    self.save_subscription(body)
                    self.respond_json(200, { 'data': { 'success': True }})
                except Exception as e:
                    print(e)
                    self.respond_error('unable-to-save-subscription',
                        'The subscription was received but we were unable to'
                        + 'save it to our database.')

    return CustomController


