import unittest
import json
import os
from datetime import datetime as dt
from .. import Journey

class TestJourney(unittest.TestCase):
    dirname = os.path.dirname(__file__)
    with open(os.path.join(dirname, 'mock_journeys.json'), 'r') as mock_journeys_f:
        mock_journeys = json.load(mock_journeys_f).get('journeys')

    def test_from_vvs(self):
        journeys = []
        for mock_json in self.mock_journeys:
           journeys.append(Journey().from_vvs(mock_json))
        self.assertTrue(len(journeys) == 3)

        for journey in journeys:
            self.assertIsNotNone(journey)
            self.assertIsInstance(journey, Journey)

        journey = journeys[0]
        self.assertEqual(journey.origin, 'Stadtmitte')
        self.assertEqual(journey.dest, 'Stuttgart Hauptbahnhof (tief)')
        self.assertEqual(len(journey.legs), 1)

    def test_to_link(self):
        dep_time = dt(2020, 3, 16, 7, 7)
        journey = Journey("de:08111:6056","de:08111:13", dep_time, None)
        self.maxDiff = None
        expected = """https://www3.vvs.de/mng/#!/XSLT_TRIP_REQUEST2@details?
                        deeplink={
                            **dateTime**:{
                                **date**:**16.03.2020**,
                                **dateFormat**:****,
                                **time**:**07:07**,
                                **timeFormat**:****,
                                **useRealTime**:true,
                                **isDeparture**:true
                            },
                            **odvs**:{
                                **orig**:**de:08111:6056**,
                                **dest**:**de:08111:13**
                            }
                        }"""
        expected = ''.join(expected.split())
        self.assertEqual(journey.to_link(), expected)
