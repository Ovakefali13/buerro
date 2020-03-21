import unittest
import os
from datetime import datetime

from usecase.lunchbreak import Lunchbreak

from services.weatherAPI.weather_service import WeatherAdapter
from services.weatherAPI.test.test_service import WeatherMock,WeatherAdapterRemote
from services.yelp.yelp_service import YelpService
from services.yelp.yelp_request import YelpRequest
from services.yelp.test.test_service import YelpMock, YelpServiceRemote
from services.maps import GeocodingService, GeocodingJSONRemote, \
    MapService, MapJSONRemote
from services.maps.test.test_service import GeocodingMockRemote, MapMockRemote
from services.cal.cal_service import CalService, iCloudCaldavRemote, Event
from services.cal.test.test_service import CalMockRemote

class TestLunchbreak(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        if 'DONOTMOCK' in os.environ:
            self.weather_adapter = WeatherAdapter.instance(
                WeatherAdapterRemote.instance())
            self.yelp_service = YelpService.instance(
                YelpServiceRemote.instance())
            self.geocoding_service = GeocodingService.instance(
                GeocodingJSONRemote.instance())
            self.map_service = MapService.instance(
                MapJSONRemote.instance())
            self.calendar_service = CalService.instance(
                CalMockRemote.instance())
        else:
            print("Mocking remotes...")
            self.weather_adapter = WeatherAdapter.instance(
                WeatherMock.instance())
            self.calendar_service = CalService.instance(
                iCloudCaldavRemote.instance())
            self.geocoding_service = GeocodingService.instance(
                GeocodingMockRemote.instance())
            self.map_service = MapService.instance(
                MapMockRemote.instance())
            self.yelp_service = YelpService.instance(
                YelpServiceRemote.instance())

        self.dhbw = (48.7735115, 9.1710448)

    @classmethod
    def setUp(self):
        self.lb = Lunchbreak()
        self.lb.set_services(
            weather_adapter=self.weather_adapter,
            yelp_service=self.yelp_service,
            geocoding_service=self.geocoding_service,
            map_service=self.map_service,
            calendar_service=self.calendar_service
        )

    def test_check_lunch_options(self):
        nearby_restaurants, start, end = self.lb.check_lunch_options(self.dhbw)
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
        ret = self.lb.wait_for_user_request("Four")
        self.assertEqual(ret, 3)
        ret = self.lb.wait_for_user_request("four")
        self.assertEqual(ret, 3)
