import unittest
import os
import json


from .. import YelpService,YelpServiceRemote


class YelpMock():

    def requestBusinesses(self):
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, 'mock_weather.json'), 'r') as mockWeather_f:
            mockWeather = json.load(mockWeather_f)
        return mockWeather


    def requestBusiness(self, id):
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, 'mock_weather_forecast.json'), 'r') as mockWeather_f:
            mockWeatherForecast = json.load(mockWeather_f)
        return mockWeatherForecast


class TestYelpService(unittest.TestCase):
    if 'DONOTMOCK' in os.environ:
        remote = YelpServiceRemote()
    else:
        print("Mocking remotes...")
        remote = YelpMock()


