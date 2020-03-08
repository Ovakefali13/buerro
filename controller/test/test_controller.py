import requests
import unittest
import time

from http.server import HTTPServer
from threading import Thread, Event

from services.Singleton import Singleton
from controller import ControllerFromArgs
from chatbot import Chatbot, Intent
from usecase import Usecase

@Singleton
class MockChatbot(Chatbot):

    def get_intent(self, message:str):
       return Intent("mock_work", [])


@Singleton
class MockUsecase(Usecase):
    def __init__(self):
        self.count == 0

    def advance(self, entities):
        self.count += 1

        if self.count == 1:
            return {
                'message': "I created reminders for you. Do you want music?"
            }
        if self.count == 2:
            return {
                'message': 'How about this Spotify playlist?'
                    + '\nWhich project do you want to work on?',
                'link': 'https://open.spotify.com/playlist/37i9dQZF1DWZeKCadgRdKQ'
            }
        if self.count == 3:
            todos = [
                'Mark 1 to n relationships in architecture',
                'Implement a prototype for browser notifications'
            ]
            return {
                'message': "Here are you Todo's: ",
                'list': todos
            }
        raise Exception("advance called too often")

class TestController(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.hostName = "localhost"
        self.serverPort = 9149
        self.server_url = "http://" + self.hostName + ":" + str(self.serverPort)

        chatbot = MockChatbot.instance()
        usecaseByContext = {
            "mock_work": MockUsecase
        }

        MockController = ControllerFromArgs(chatbot, usecaseByContext)
        self.httpd = HTTPServer((self.hostName, self.serverPort),
            MockController)

        self.ready_event = Event()
        self.shutdown_event = Event()
        def in_thread():
            self.ready_event.set()
            while not self.shutdown_event.is_set():
                self.httpd.handle_request()

        self.server_thread = Thread(target=in_thread)
        self.server_thread.start()

        time.sleep(0.0001)
        self.ready_event.wait(3)
        if not self.ready_event.is_set():
            raise Exception("most likely failed to start server")

    def test_ping_pong(self):
        res = requests.post(self.server_url, data={"message": "ping"})
        self.assertEqual(res.content, b"pong")

    def test_can_step_through_usecase(self):
        def _query(message:str):
            whole_res = requests.post(self.server_url, data={"message":message})
            return whole_res.get('message')

        res = _query("Set up my work environment")
        self.assertIn(b"music?", res)
        res = _query("Yes, I do.")
        self.assertIn(b"Which project do you want to work on?", res)
        res = _query("ASE")
        self.assertIn(b"Todo", res)

    @classmethod
    def tearDownClass(self):
        self.shutdown_event.set()
        requests.post(self.server_url, data={'message':'shutdown'})
        self.server_thread.join(0.1)
