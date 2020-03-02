import unittest
from .. import VVSAdapter, VVSRemote, VVSEfaJSONRemote
import os

class VVSMockRemote(VVSRemote):
    def get_locations(self, location:str):
        locations = [
            {
                'id': 'de:08111:6118',
                'name': 'Stuttgart, Hauptbahnhof',
                'isBest': True,
            },
            {
                'id': 'wrongID',
                'name': 'something else',
                'isBest': False
            }
        ]
        return locations

    def get_journeys(self):
        return None # TODO return a few mock journeys

class TestVVSAdapter(unittest.TestCase):
    if 'DONOTMOCK' in os.environ: 
        remote = VVSEfaJSONRemote()
    else:
        remote = VVSMockRemote()

    vvs_adapter = VVSAdapter(remote)
    
    def test_get_location(self):
        location_id = self.vvs_adapter.get_location_id("Stuttgart Hauptbahnhof")
        self.assertEqual(location_id, 'de:08111:6118')


