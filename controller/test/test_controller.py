import requests
import unittest
import time

from http.server import HTTPServer
from threading import Thread, Event

from .. import Controller

class TestController(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.hostName = "localhost"
        self.serverPort = 8089
        self.server_url = "http://" + self.hostName + ":" + str(self.serverPort)
        self.controller = HTTPServer((self.hostName, self.serverPort), Controller)

        self.ready_event = Event()
        self.shutdown_event = Event()
        def in_thread():
            self.ready_event.set()
            while not self.shutdown_event.is_set():
                self.controller.handle_request()

        self.server_thread = Thread(target=in_thread)
        self.server_thread.start()

        time.sleep(0.0001)
        self.ready_event.wait(3)
        if not self.ready_event.is_set():
            raise Exception("most likely failed to start server")

    def test_post_message(self):
        resp = requests.post(self.server_url, data={"message": "ping"})
        self.assertEqual(resp.content, b"pong")

    @classmethod
    def tearDown(self):
        self.shutdown_event.set()
        requests.post(self.server_url, data={'message':'shutdown'})
        self.server_thread.join(0.1)
