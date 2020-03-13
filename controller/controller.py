from chatbot import Chatbot, Intent
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
import json

from . import NotificationHandler

#usecaseByContext = { "work": SetupWork , ... }
#Controller = ControllerFromArgs(WatsonChatbot(), usecaseByContext)

def ControllerFromArgs(chatbot:Chatbot, usecaseByContext:dict):
    class CustomController(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.notification_handler = NotificationHandler.instance()
            self.chatbot = chatbot
            self.usecaseByContext = usecaseByContext
            super(CustomController, self).__init__(*args, **kwargs)

        def do_POST(self):
            def _set_headers(http_code:int):
                self.send_response(http_code)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

            def _respond(msg:str):
                self.wfile.write(msg.encode("utf-8"))

            def _shutdown():
                _set_headers(200)
                _respond('shutdown')

            length = int(self.headers['Content-Length'])
            body = urllib.parse.parse_qs(self.rfile.read(length).decode('utf-8'))

            msg = body.get('message', '')[0]
            if msg == 'ping':
                _set_headers(200)
                _respond('pong')
            elif msg == 'shutdown':
                _shutdown()
            else:
                intent = self.chatbot.get_intent(msg)
                usecase = self.usecaseByContext.get(intent.context, None)
                if usecase:
                    usecase = usecase.instance()
                    reply = usecase.advance(intent.entities)

                    _set_headers(200)
                    _respond(json.dumps(reply))
                else:
                    _set_headers(400)
            del msg

        def do_GET(self):
            def _set_headers(http_code:int):
                self.send_response(http_code)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

            def _respond(msg:str):
                self.wfile.write(msg.encode("utf-8"))

            if self.path == '/notification':
                # block until event: threading.Lock, threading.Event
                notification = self.notification_handler.wait()

                _set_headers(200)
                _respond(notification)

    return CustomController



