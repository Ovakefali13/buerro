import unittest
import os
from datetime import datetime
from unittest.mock import patch
from usecase.lunchbreak import Lunchbreak

from services.weatherAPI.weather_service import WeatherAdapter
from services.weatherAPI.test.test_service import WeatherMock, WeatherAdapterRemote
from services.yelp.yelp_service import YelpService
from services.yelp.yelp_request import YelpRequest
from services.yelp.test.test_service import YelpMock, YelpServiceRemote
from services.maps import (
    GeocodingService,
    GeocodingJSONRemote,
    MapService,
    MapJSONRemote,
)
from services.maps.test.test_service import GeocodingMockRemote, MapMockRemote
from services.cal.cal_service import CalService, iCloudCaldavRemote, Event
from services.cal.test.test_service import CalMockRemote
from handler import LocationHandler, NotificationHandler


class TestLunchbreak(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        if "DONOTMOCK" in os.environ:
            self.weather_adapter = WeatherAdapter.instance(
                WeatherAdapterRemote.instance()
            )
            self.yelp_service = YelpService.instance(YelpServiceRemote.instance())
            self.geocoding_service = GeocodingService.instance(
                GeocodingJSONRemote.instance()
            )
            self.map_service = MapService.instance(MapJSONRemote.instance())
            self.calendar_service = CalService.instance(iCloudCaldavRemote.instance())
        else:
            print("Mocking remotes...")
            self.weather_adapter = WeatherAdapter.instance(WeatherMock.instance())
            self.calendar_service = CalService.instance(CalMockRemote.instance())
            self.geocoding_service = GeocodingService.instance(
                GeocodingMockRemote.instance()
            )
            self.map_service = MapService.instance(MapMockRemote.instance())
            self.yelp_service = YelpService.instance(YelpMock.instance())

        self.dhbw = (48.7735115, 9.1710448)

    @classmethod
    def setUp(self):
        self.lb = Lunchbreak()
        self.lb.set_services(
            weather_adapter=self.weather_adapter,
            yelp_service=self.yelp_service,
            geocoding_service=self.geocoding_service,
            map_service=self.map_service,
            calendar_service=self.calendar_service,
        )

    @patch.object(LocationHandler.instance(), "get")
    def test_advance(self, location_mock):
        location_mock.return_value = (48.76533759999999, 9.161932799999999)
        message = self.lb.advance("Where can I eat for lunch?")
        self.assertIsInstance(message, dict)
        self.assertIsInstance(message["dict"], dict)
        self.assertFalse(self.lb.is_finished())
        message = self.lb.advance("I would like to eat at restaurant number one")
        self.assertIsInstance(message, dict)
        self.assertIsInstance(message["message"], str)
        self.assertTrue(self.lb.is_finished())

    @patch.object(LocationHandler.instance(), "get")
    def test_notify(self, location_mock):
        location_mock.return_value = (48.76533759999999, 9.161932799999999)
        is_active = self.lb.hours_until_lunch()
        self.assertIsInstance(is_active, bool)

    @patch.object(NotificationHandler.instance(), "push")
    @patch.object(LocationHandler.instance(), "get")
    def test_trigger_proactive_usecase(self, location_mock, mock_push):
        location_mock.return_value = 48.76533759999999, 9.161932799999999
        is_triggered = self.lb.trigger_proactive_usecase()
        self.assertIsInstance(is_triggered, bool)
        if is_triggered:
            message = self.lb.advance("I would like to eat at restaurant number one")
            self.assertIsInstance(message, dict)
            self.assertIsInstance(message["message"], str)
            self.assertTrue(self.lb.is_finished())
            mock_push.assert_called_once()
