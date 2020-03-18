import unittest
import os
import json
from datetime import datetime as dt, timedelta
import pytz

from .. import VVSService, VVSRemote, VVSEfaJSONRemote, Journey, JourneyRequest

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

    @classmethod
    def setUpClass(self):
        if 'DONOTMOCK' in os.environ:
            self.remote = VVSEfaJSONRemote()
        else:
            print("Mocking remotes...")
            self.remote = VVSMockRemote()

        self.vvs_service = VVSService.instance()
        self.vvs_service.set_remote(self.remote)

    def test_get_location(self):
        location_id = self.vvs_service.get_location_id("Stuttgart Hauptbahnhof")
        self.assertEqual(location_id, 'de:08111:6118')

    def test_get_journeys(self):
        req_time = dt(2020, 3, 2, 9, 0)

        journeys = self.vvs_service.get_journeys(
            "Stuttgart Hauptbahnhof", "Rotebühlplatz", "arr", req_time)
        self.assertIsNotNone(journeys)
        self.assertTrue(len(journeys) > 0)

    def test_recommend_journey(self):
        now = dt.now(pytz.utc)
        event_start = now + timedelta(minutes=20)
        journeys = []

        dep1 = now
        arr1 = dep1 + timedelta(minutes=11)
        journey1 = Journey('A', 'B', dep1, arr1)
        journeys.append(journey1)

        dep2 = now + timedelta(minutes=1)
        arr2 = dep2 + timedelta(minutes=5)
        journey2 = Journey('A', 'B', dep2, arr2)
        journeys.append(journey2)

        with self.subTest("earlier, but significantly shorter wins"):
            journey = self.vvs_service.recommend_journey_to_arrive_by(
                journeys, event_start)
            self.assertEqual(journey, journey2)

        dep3 = event_start - timedelta(minutes=1)
        arr3 = dep3 + timedelta(minutes=4)
        journey3 = Journey('A', 'B', dep3, arr3)
        journeys.append(journey3)

        with self.subTest("even shorter, but too late"):
            journey = self.vvs_service.recommend_journey_to_arrive_by(
                journeys, event_start)
            self.assertEqual(journey, journey2)

        dep4 = event_start - timedelta(minutes=6)
        arr4 = dep4 + timedelta(minutes=5)
        journey4 = Journey('A', 'B', dep4, arr4)
        journeys.append(journey4)

        with self.subTest("same duration and just in time wins"):
            journey = self.vvs_service.recommend_journey_to_arrive_by(
                journeys, event_start)
            self.assertEqual(journey, journey4)

