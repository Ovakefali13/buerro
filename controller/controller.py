
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib


class Controller(BaseHTTPRequestHandler):
    """
    headers = {
        'Content-type', 'application/json'
    }
    """

    def do_POST(self):
        def _set_headers():
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def respond(msg:str):
            self.wfile.write(msg.encode("utf-8"))

        def _shutdown():
            _set_headers()
            respond('shutdown')

        length = int(self.headers['Content-Length'])
        body = urllib.parse.parse_qs(self.rfile.read(length).decode('utf-8'))
        msg = body.get('message', '')[0]
        if msg == 'ping':
            _set_headers()
            respond('pong')
        elif msg == 'shutdown':
            _shutdown()
        else:
            self.send_response(400)
            self.end_headers()
        del msg



