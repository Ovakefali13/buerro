import requests
import unittest

from http.server import HTTPServer
from socketserver import ThreadingMixIn

from .. import Controller

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread"""

class TestController(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.hostName = "localhost"
        self.serverPort = "8089"

        self.controller = ThreadedHTTPServer((hostName, serverPort), Controller)
        print("Server started http://%s:%s" % (hostName, serverPort))
        self.controller.serve_forever()

    def test_post_message(self):
        url = self.hostName + ":" + self.serverPort
        resp = requests.post(url, data="ping")
        self.assertEqual(resp, "pong")
