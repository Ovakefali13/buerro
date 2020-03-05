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
       if "work" in message:
           return Intent("mock_work", [])

@Singleton
class MockUsecase(Usecase):
    def advance(self, entities):
        return "I created reminders for you"

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
        resp = requests.post(self.server_url, data={"message": "ping"})
        self.assertEqual(resp.content, b"pong")

    def test_get_answer(self):
        message = "Set up my work environment"
        resp = requests.post(self.server_url, data={"message":message})
        self.assertEqual(resp.content,b"I created reminders for you")


    @classmethod
    def tearDownClass(self):
        self.shutdown_event.set()
        requests.post(self.server_url, data={'message':'shutdown'})
        self.server_thread.join(0.1)
