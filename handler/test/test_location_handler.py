from .. import LocationHandler
import unittest

class TestLocationHandler(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.location_handler = LocationHandler.instance()
        self.location_handler.set_db('handler/test/test.db')

    def test_set_and_get(self):
        lat, lon = 10.1920, 42.0815
        self.location_handler.set(lat, lon)
        g_lat, g_lon = self.location_handler.get()
        self.assertEqual((g_lat, g_lon), (lat, lon))
