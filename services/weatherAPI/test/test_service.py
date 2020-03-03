import unittest
import os
import json

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


class TestWeatherService:

    pass
    # if 'DONOTMOCK' in os.environ:
    #     remote = VVSEfaJSONRemote()
    # else:
    #     print("Mocking remotes...")
    #     remote = WeatherMock()



