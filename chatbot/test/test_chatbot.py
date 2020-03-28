import unittest
from .. import Chatbot, BuerroBot

from usecase import Lunchbreak

class TestChatbot(unittest.TestCase):

    buerro_bot = BuerroBot()
    chatbot = Chatbot(buerro_bot)

    def test_chatbot_handles_empty_string(self):
        response = self.chatbot.get_usecase("")
        self.assertEquals(response, None)

    def test_chatbot_handles_none(self):
        response = self.chatbot.get_usecase(None)
        self.assertEquals(response, None)

    def test_chatbot_recognizes_keyword(self):
        response = self.chatbot.get_usecase("bla bla lunch bla bla")
        self.assertEquals(response, Lunchbreak)
