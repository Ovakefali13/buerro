import requests
import unittest
import time
import json
from http.server import HTTPServer
from threading import Thread, Event

from services.singleton import Singleton
from controller import ControllerFromArgs, LocationHandler
from chatbot import ChatbotBehavior, Chatbot
from usecase import Usecase, Reply

@Singleton
class MockChatbotBehavior(ChatbotBehavior):

    def get_intent(self, message:str):
        return "mock_work"

    def clear_context(self):
        pass

class MockUsecase(Usecase):
    def __init__(self):
        self.count = 0

    def advance(self, message):
        self.count += 1

        if self.count == 1:
            return Reply("I created reminders for you. Do you want music?")
        if self.count == 2:
            return Reply({
                'message': 'How about this Spotify playlist?'
                    + '\nWhich project do you want to work on?',
                'link': 'https://open.spotify.com/playlist/37i9dQZF1DWZeKCadgRdKQ'
            })
        if self.count == 3:
            todos = [
                'Mark 1 to n relationships in architecture',
                'Implement a prototype for browser notifications'
            ]
            return Reply({
                'message': "Here are you Todo's: ",
                'list': todos
            })
        raise Exception("advance called too often")

    def reset(self):
        self.count = 0

    def is_finished(self):
        if self.count == 3:
            return True
        return False

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

    def test_can_step_through_usecase(self):
        def _query(message:str):
            body = {"message": message}
            res = requests.post(self.server_url + '/message', json=body)
            res = res.json()
            self.assertIsNotNone(res.get('success'))
            return res.get('message', '')

        res = _query("Set up my work environment")
        self.assertIn("music?", res)
        res = _query("Yes, I do.")
        self.assertIn("Which project do you want to work on?", res)
        res = _query("ASE")
        self.assertIn("Todo", res)

    def test_update_location(self):
        def _query(lat, lon):
            body = {"location": [lat, lon]}
            res = requests.post(self.server_url + '/location', json=body)
            res = res.json()
            self.assertIsNotNone(res.get('success'))
            return res

        location_handler = LocationHandler.instance()
        location_handler.set_db('controller/test/test.db')

        lat, lon = 53.47554, 9.69618
        _query(lat, lon)
        g_lat, g_lon = location_handler.get()
        self.assertEqual(lat, g_lat)
        self.assertEqual(lon, g_lon)

        lat, lon = 52.3086091, 9.8328946
        _query(lat, lon)
        g_lat, g_lon = location_handler.get()
        self.assertEqual(lat, g_lat)
        self.assertEqual(lon, g_lon)

    @classmethod
    def tearDownClass(self):
        self.shutdown_event.set()
        body = {'message': 'shutdown'}
        requests.post(self.server_url + '/message', json=body)
