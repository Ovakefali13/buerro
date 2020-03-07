import unittest
import os
import json

from .. import WeatherAdapter, WeatherAdapterRemote, WeatherAdapterModule

class WeatherMock(WeatherAdapterModule):

    def updateCurrentWeatherByCity(self, city):
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, 'mock_weather.json'), 'r') as mockWeather_f:
            mockWeather = json.load(mockWeather_f)
        return mockWeather


    def updateWeatherForecastByCity(self, city):
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, 'mock_weather_forecast.json'), 'r') as mockWeather_f:
            mockWeatherForecast = json.load(mockWeather_f)
        return mockWeatherForecast


class TestWeatherService(unittest.TestCase):
    city = 'Stuttgart'

    if 'DONOTMOCK' in os.environ:
        remote = WeatherAdapterRemote()
    else:
        print("Mocking remotes...")
        remote = WeatherMock()

    weatherAdapter = WeatherAdapter.instance()
    weatherAdapter.setRemote(remote)

    #def test_update(self):
    #   self.weatherAdapter.update('Stuttgart')

    #def test_updateCurrentWeatherByCity(self):
    #    weather = self.weatherAdapter.updateCurrentWeatherByCity(self.city)


    #def test_updateWeatherForecastByCity(self):
    #    weatherForecast = self.weatherAdapter.updateWeatherForecastByCity(self.city)


    def test_getCurrentTemperature(self):
        self.weatherAdapter.setRemote(self.remote)
        self.weatherAdapter.update(self.city)
        temp = self.weatherAdapter.getCurrentTemperature()
        self.assertGreater(temp, -50)
        self.assertLess(temp, 50)

    def test_getCurrentWeather(self):
        self.weatherAdapter.update(self.city)
        weather = self.weatherAdapter.getCurrentWeather()
        self.assertIsInstance(weather, str)

    def test_getForecastWeather(self):
        self.weatherAdapter.update(self.city)
        weather = self.weatherAdapter.getForecastWeather(3)
        self.assertIsInstance(weather, str)

    def test_isBadWeather(self):
        self.weatherAdapter.update(self.city)
        isWeatherBad = self.weatherAdapter.isBadWeather()
        self.assertTrue(isWeatherBad)

    def test_willBeBadWeather(self):
        #TODO How to test
        self.weatherAdapter.update(self.city)
        willBeBadWeather = self.weatherAdapter.willBeBadWeather(3)
        self.assertTrue(willBeBadWeather)

        willBeBadWeather = self.weatherAdapter.willBeBadWeather(6)
        self.assertTrue(willBeBadWeather)

        willBeBadWeather = self.weatherAdapter.willBeBadWeather(9)
        self.assertTrue(willBeBadWeather)






