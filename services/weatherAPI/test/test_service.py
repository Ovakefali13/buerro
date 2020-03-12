import unittest
import os
import json

from .. import WeatherAdapter, WeatherAdapterRemote, WeatherAdapterModule

class WeatherMock(WeatherAdapterModule):

    def update_current_weather_by_city(self, city):
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, 'mock_weather.json'), 'r') as mockWeather_f:
            mock_weather = json.load(mockWeather_f)
        return mock_weather


    def update_weather_forecast_by_city(self, city):
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, 'mock_weather_forecast.json'), 'r') as mockWeather_f:
            mock_weather_forecast = json.load(mockWeather_f)
        return mock_weather_forecast


class TestWeatherService(unittest.TestCase):
    city = 'Stuttgart'

    if 'DONOTMOCK' in os.environ:
        remote = WeatherAdapterRemote()
    else:
        print("Mocking remotes...")
        remote = WeatherMock()

    weather_adapter = WeatherAdapter.instance()
    weather_adapter.set_remote(remote)

    def test_get_current_temperature(self):
        self.weather_adapter = WeatherAdapter.instance()
        self.weather_adapter.set_remote(self.remote)
        self.weather_adapter.update(self.city)
        temp = self.weather_adapter.get_current_temperature()
        self.assertGreater(temp, -50)
        self.assertLess(temp, 50)

    def test_get_current_weather(self):
        self.weather_adapter = WeatherAdapter.instance()
        self.weather_adapter.set_remote(self.remote)
        self.weather_adapter.update(self.city)
        weather = self.weather_adapter.get_current_weather()
        self.assertIsInstance(weather, str)

    def test_get_forecast_weather(self):
        self.weather_adapter = WeatherAdapter.instance()
        self.weather_adapter.set_remote(self.remote)
        self.weather_adapter.update(self.city)
        weather = self.weather_adapter.get_forecast_weather(3)
        self.assertIsInstance(weather, str)

    def test_is_bad_weather(self):
        self.weather_adapter = WeatherAdapter.instance()
        self.weather_adapter.set_remote(self.remote)
        self.weather_adapter.update(self.city)
        is_weather_bad = self.weather_adapter.is_bad_weather()
        self.assertIsInstance(is_weather_bad, bool)

    def test_will_be_bad_weather(self):
        #TODO How to test
        self.weather_adapter = WeatherAdapter.instance()
        self.weather_adapter.set_remote(self.remote)
        self.weather_adapter.update(self.city)
        will_be_bad_weather = self.weather_adapter.will_be_bad_weather(3)
        self.assertIsInstance(will_be_bad_weather, bool)






