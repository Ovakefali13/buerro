import unittest
from datetime import datetime, timedelta
from freezegun import freeze_time
from unittest.mock import patch
from unittest import skipIf
import os
import json

from usecase.usecase import Reply
from usecase.transport import Transport
from services.weatherAPI import WeatherAdapter
from services.maps import GeocodingService, MapService
from services.vvs import VVSService

class TestTransport(unittest.TestCase):
    dhbw = [48.773563, 9.170963]
    mensa = [48.780834, 9.169989]
            
    @classmethod
    def setUpClass(self):
        self.use_case = Transport()

    @skipIf('DONOTMOCK' not in os.environ, reason = 'Mocking does not make sense since a vast amount of APIs is required with each of them depending on each other.')
    @freeze_time('2020-03-26 21:30:00')
    @patch.object(WeatherAdapter._decorated, 'is_bad_weather', return_value=False)
    def test_usecase(self, is_bad_weather):
        with open(os.path.join(os.path.dirname(__file__), 'mock_data.json'), 'r') as f:
            mock_route = json.load(f)

        for route in mock_route:
            temp = route['req_info']
            mock_req_info = {                
                'Start': tuple(temp['Start']),
                'Dest': tuple(temp['Dest']),
                'ArrDep': temp['ArrDep'],
                'Time': datetime(2020, 3, temp['Day'], temp['Hour'], temp['Minute'])
            }       
            mock_reply = route['reply']
            mock_sentence = route['sentence']
            
            reply = self.use_case.advance(mock_sentence)

            # Check if the request information is correct
            self.assertEqual(mock_req_info, self.use_case.req_info)

            # Check if reply is corret
            self.assertIsInstance(reply, Reply)