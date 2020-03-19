import unittest
from datetime import datetime
from usecase.lunchbreak import Lunchbreak
import os
from services.cal.event import Event


class TestLunchbreak(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        if 'DONOTMOCK' in os.environ:
            self.MOCK = False
        else:
            print("Mocking remotes...")
            self.MOCK = True
        self.MOCK_LOCATION = [48.76533759999999, 9.161932799999999]
        self.dhbw = [48.773563, 9.170963]

    @classmethod
    def setUp(self):
        self.lb = Lunchbreak()
        if(self.MOCK):
            self.lb.set_mock_remotes()

    def test_check_lunch_options(self):
        nearby_restaurants, start, end, duration = self.lb.check_lunch_options(self.dhbw)
        self.assertIsInstance(nearby_restaurants, list)

    def test_time_diff_in_hours(self):
        start = '2020-05-05T12:00:00'
        start_iso = datetime.fromisoformat(start)

        end = '2020-05-06T12:00:00'
        end_iso = datetime.fromisoformat(end)

        diff_hours = self.lb.time_diff_in_hours(end_iso, start_iso)
        self.assertEqual(diff_hours, 24)

    def test_open_maps_route(self):
        nearby_restaurants, start, end = self.lb.check_lunch_options(self.dhbw)
        google_link = self.lb.open_maps_route(self.dhbw, nearby_restaurants[1])
        self.assertIsInstance(google_link, str)

    def test_notify(self):
        is_active = self.lb.notify()
        self.assertIsInstance(is_active, bool)

    def test_create_cal_event(self):
        nearby_restaurants, start, end = self.lb.check_lunch_options(self.dhbw)
        google_link = self.lb.open_maps_route(self.dhbw, nearby_restaurants[1])
        ret = self.lb.create_cal_event(start,end, nearby_restaurants[1], google_link)
        self.assertIsInstance(ret, Event)

    def test_wait_for_user_input(self):
        ret = self.lb.evaluate_user_request("Four")
        self.assertEqual(ret, 3)
        ret = self.lb.evaluate_user_request("four")
        self.assertEqual(ret, 3)