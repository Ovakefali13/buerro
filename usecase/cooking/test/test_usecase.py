import unittest
import datetime
from usecase.cooking import Cook

class TestCooking(unittest.TestCase):
    MOCK_LOCATION = 'Jägerstraße 56, 70174 Stuttgart'
    use_case = None

    @classmethod
    def setUpClass(self):
        self.use_case = Cook()

    def test_trigger_usecase(self):
        self.use_case.trigger_use_case('pork')

        response_message = self.use_case.get_response()

        self.assertIs(type(response_message), str)
    
    def test_not_time_to_cook(self):
        self.use_case.not_time_to_cook()

        response_message = self.use_case.get_response()

        self.assertIs(type(response_message), str)
        self.assertEquals(response_message[0] + response_message[1] + response_message[2], "A r")