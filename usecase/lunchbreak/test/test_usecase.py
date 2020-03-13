import unittest
from datetime import datetime
from usecase.lunchbreak import Lunchbreak
import os


class TestLunchbreak(unittest.TestCase):

    if 'DONOTMOCK' in os.environ:
        MOCK = False
    else:
        print("Mocking remotes...")
        MOCK = True
    MOCK_LOCATION = [48.76533759999999, 9.161932799999999]
    dhbw = [48.773563, 9.170963]

    def test_check_lunch_options(self):
        lb = Lunchbreak(self.MOCK)
        nearby_restaurants = lb.check_lunch_options(self.dhbw)
        self.assertIsInstance(nearby_restaurants, list)

    def test_time_diff_in_hours(self):
        lb = Lunchbreak(self.MOCK)
        start = '2020-05-05T12:00:00'
        start_iso = datetime.fromisoformat(start)

        end = '2020-05-06T12:00:00'
        end_iso = datetime.fromisoformat(end)

        diff_hours = lb.time_diff_in_hours(end_iso, start_iso)
        self.assertEqual(diff_hours, 24)

    def test_open_maps_route(self):
        lb = Lunchbreak(self.MOCK)
        nearby_restaurants = lb.check_lunch_options(self.dhbw)

        google_link = lb.open_maps_route(1,self.dhbw, nearby_restaurants)
        self.assertIsInstance(google_link, str)

    def test_notify(self):
        lb = Lunchbreak(self.MOCK)
        is_active = lb.notify()

        self.assertIsInstance(is_active, bool)
