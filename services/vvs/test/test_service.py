import unittest
from .. import VVSService, VVSRemote, VVSEfaJSONRemote, Journey, JourneyRequest
import os
import json
from datetime import datetime, timedelta

class VVSMockRemote(VVSRemote):

    def get_locations(self, location:str):
        invalid_location = {
            'id': 'wrongID',
            'name': 'something else',
            'isBest': False
        }
        if location == "Stuttgart Hauptbahnhof":
            return [
                {
                    'id': 'de:08111:6118',
                    'name': 'Stuttgart, Hauptbahnhof',
                    'isBest': True,
                },
                invalid_location
            ]
        elif location == "Rotebühlplatz":
            return [
                {
                    'id': 'de:08111:6056',
                    'name': 'Stadtmitte',
                    'isBest': True,
                },
                invalid_location
            ]
        return []

    def get_journeys(self, req:JourneyRequest):
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, 'mock_journeys.json'), 'r') as mock_journeys_f:
            mock_journeys = json.load(mock_journeys_f).get('journeys')

        return mock_journeys

class TestVVSService(unittest.TestCase):
    if 'DONOTMOCK' in os.environ:
        remote = VVSEfaJSONRemote()
    else:
        print("Mocking remotes...")
        remote = VVSMockRemote()

    vvs_service = VVSService(remote)

    def test_get_location(self):
        location_id = self.vvs_service.get_location_id("Stuttgart Hauptbahnhof")
        self.assertEqual(location_id, 'de:08111:6118')

    def test_get_journeys(self):
        req_time = datetime(2020, 3, 2, 9, 0)

        journeys = self.vvs_service.get_journeys("Stuttgart Hauptbahnhof", "Rotebühlplatz", "arr", req_time)
        self.assertIsNotNone(journeys)
        self.assertTrue(len(journeys) > 0)
