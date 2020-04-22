import unittest
from unittest.mock import patch

from .. import LocationHandler
from services import PrefService


class TestLocationHandler(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.location_handler = LocationHandler.instance()

    def test_set_and_get(self):
        lat, lon = 10.1920, 42.0815
        self.location_handler.set_db("handler/test.db")
        self.location_handler.set(lat, lon)
        g_lat, g_lon = self.location_handler.get()
        self.assertEqual((g_lat, g_lon), (lat, lon))

    @patch.object(PrefService, "get_specific_pref")
    def test_defaults_to_home(self, mock_get_pref):
        home = (48.785496, 9.210121)
        mock_get_pref.return_value = home

        self.location_handler.set_db("handler/non_existent_db.db")

        location = self.location_handler.get()
        self.assertEqual(location, home)
