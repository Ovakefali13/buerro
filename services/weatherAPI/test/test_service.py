import unittest
import os
import json

from .. import WeatherAdapter



class WeatherMock():

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
    weatherAdapter = WeatherAdapter.instance()
    weatherAdapter.setRemote(WeatherMock())

    #def test_update(self):
    #   self.weatherAdapter.update('Stuttgart')

    #def test_updateCurrentWeatherByCity(self):
    #    weather = self.weatherAdapter.updateCurrentWeatherByCity(self.city)


    #def test_updateWeatherForecastByCity(self):
    #    weatherForecast = self.weatherAdapter.updateWeatherForecastByCity(self.city)


    def test_getCurrentTemperature(self):
        self.weatherAdapter.update(self.city)
        temp = self.weatherAdapter.getCurrentTemperature()
        self.assertEqual(temp, 2.34)

    def test_getCurrentWeather(self):
        self.weatherAdapter.update(self.city)
        weather = self.weatherAdapter.getCurrentWeather()
        self.assertEquals(weather, 'Clouds')

    def test_isBadWeather(self):
        self.weatherAdapter.update(self.city)
        isWeatherBad = self.weatherAdapter.isBadWeather()
        self.assertTrue(isWeatherBad)

    def test_willBeBadWeather(self):
        self.weatherAdapter.update(self.city)
        willBeBadWeather = self.weatherAdapter.willBeBadWeather(3)
        self.assertTrue(willBeBadWeather)

        willBeBadWeather = self.weatherAdapter.willBeBadWeather(6)
        self.assertTrue(willBeBadWeather)

        willBeBadWeather = self.weatherAdapter.willBeBadWeather(9)
        self.assertTrue(willBeBadWeather)


    # if 'DONOTMOCK' in os.environ:
    #     remote = VVSEfaJSONRemote()
    # else:
    #     print("Mocking remotes...")
    #     remote = WeatherMock()



