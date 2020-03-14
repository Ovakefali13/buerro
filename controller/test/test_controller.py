import requests
import unittest
import time
import json
from http.server import HTTPServer
from threading import Thread, Event

from services.singleton import Singleton
from controller import ControllerFromArgs
from chatbot import ChatbotBehavior, Chatbot, Intent
from usecase import Usecase

@Singleton
class MockChatbotBehavior(ChatbotBehavior):

    def get_intent(self, message:str):
        return Intent("mock_work", [])

    def clear_context(self):
        pass

    def clear_context(self):
        pass


@Singleton
class MockUsecase(Usecase):
    def __init__(self):
        self.count = 0

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

        chatbot = Chatbot(MockChatbotBehavior.instance())
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
        body = {"message": "ping"}
        res = requests.post(self.server_url + '/message', json=body)
        self.assertEqual(res.text, "pong")

    def test_can_step_through_usecase(self):
        def _query(message:str):
            body = {"message": message}
            whole_res = requests.post(self.server_url + '/message', json=body)
            return whole_res.json().get('message')

        res = _query("Set up my work environment")
        self.assertIn("music?", res)
        res = _query("Yes, I do.")
        self.assertIn("Which project do you want to work on?", res)
        res = _query("ASE")
        self.assertIn("Todo", res)

    @classmethod
    def tearDownClass(self):
        self.shutdown_event.set()
        body ={'message': 'shutdown'}
        requests.post(self.server_url + '/message', json=body)
