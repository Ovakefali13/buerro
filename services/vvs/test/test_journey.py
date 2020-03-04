import unittest
import json
import os
from datetime import datetime
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
