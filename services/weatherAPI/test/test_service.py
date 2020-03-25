import unittest
import os
import json

from util import Singleton
from .. import WeatherAdapter, WeatherAdapterRemote, WeatherAdapterModule

@Singleton
class WeatherMock(WeatherAdapterModule):

    def get_current_weather_by_city(self, city):
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, 'mock_weather.json'), 'r') as mockWeather_f:
            mock_weather = json.load(mockWeather_f)
        return mock_weather


    def get_weather_forecast_by_city(self, city):
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, 'mock_weather_forecast.json'), 'r') as mockWeather_f:
            mock_weather_forecast = json.load(mockWeather_f)
        return mock_weather_forecast

    def get_current_weather_by_coordinates(self, coordinates):
       return self.get_current_weather_by_city(self, 'Stuttgart')

    def get_weather_forecast_by_coordinates(self, coordinates):
       return self.get_weather_forecast_by_city(self, 'Stuttgart')


class TestWeatherService(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.remote = None
        if 'DONOTMOCK' in os.environ:
            self.weather_adapter = WeatherAdapter.instance(
                WeatherMock.instance())
        else:
            print("Mocking remotes...")
            self.weather_adapter = WeatherAdapter.instance(
                WeatherAdapterRemote.instance())

        self.weather_adapter.update(city='Stuttgart')

    @classmethod
    def setUp(self):
        pass

    def test_get_current_temperature(self):
        temp = self.weather_adapter.get_current_temperature()
        self.assertGreater(temp, -50)
        self.assertLess(temp, 50)

    def test_get_current_weather(self):
        weather = self.weather_adapter.get_current_weather()
        self.assertIsInstance(weather, str)

    def test_get_forecast_weather(self):
        weather = self.weather_adapter.get_forecast_weather(3)
        self.assertIsInstance(weather, str)

    def test_is_bad_weather(self):
        is_weather_bad = self.weather_adapter.is_bad_weather()
        self.assertIsInstance(is_weather_bad, bool)

    def test_will_be_bad_weather(self):
        will_be_bad_weather = self.weather_adapter.will_be_bad_weather(3)
        self.assertIsInstance(will_be_bad_weather, bool)

    def test_can_work_with_coordinates(self):
        lat, lon = 52.520007, 13.404954
        self.weather_adapter.update(coordinates=(lat, lon))
        self.assertIsInstance(self.weather_adapter.will_be_bad_weather(3),
                            bool)
