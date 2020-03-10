import unittest
from .. import Chatbot, ChatbotBehaviour, BuerroBot

class TestChatbot(unittest.TestCase):

    buerro_bot = BuerroBot()
    chatbot = Chatbot(buerro_bot)

    def test_chatbot_handles_empty_string(self):
        response = self.chatbot.get_response("")
        self.assertEquals(response, "$$undefined_behaviour")

    def test_chatbot_handles_none(self):
        response = self.chatbot.get_response(None)
        self.assertEquals(response, "$$undefined_behaviour")

    def test_chatbot_recognizes_keyword(self):
        response = self.chatbot.get_response("bla bla kalender bla bla")
        self.assertEquals(response, "$$next_calendar_event")
    
    def test_chatbot_recognizes_complex_keyword(self):
        response = self.chatbot.get_response("bla bla bla bahn bla universität")
        self.assertEquals(response, "$$next_train_to_university")
    
    def test_chatbot_undefined_behaviour(self):
        response = self.chatbot.get_response("bla bla bla bahn bla")
        self.assertEquals(response, "$$undefined_behaviour")

    def text_chatbot_clear_context(self):
        self.chatbot.behaviour.clear_context()
        self.assertEquals(self.chatbot.behaviour.context, None)