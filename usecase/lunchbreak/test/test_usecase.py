import unittest
import datetime
from usecase.lunchbreak import Lunchbreak

class TestLunchbreak(unittest.TestCase):
    MOCK_LOCATION = 'Jägerstraße 56, 70174 Stuttgart'

    def test_check_lunch_options(self):
        lb = Lunchbreak(True)
        nearby_restaurants = lb.check_lunch_options(self.MOCK_LOCATION)
        self.assertIsInstance(nearby_restaurants, list)

    def test_time_diff_in_hours(self):
        lb = Lunchbreak(True)
        start = '2020-05-05T12:00:00'
        start_iso = datetime.fromisoformat(start)

        end = '2020-05-06T12:00:00'
        end_iso = datetime.fromisoformat(end)

        diff_hours = lb.time_diff_in_hours(start_iso, end_iso)

        self.assertEqual(diff_hours, 24)

    def test_open_maps_route(self):
        lb = Lunchbreak(True)
        nearby_restaurants = lb.check_lunch_options(self.MOCK_LOCATION)

        google_link = lb.open_maps_route(1)
        self.assertIsInstance(google_link, str)

    def test_notify(self):
        lb = Lunchbreak(True)
        is_active = lb.notify()

        self.assertIsInstance(is_active, bool)