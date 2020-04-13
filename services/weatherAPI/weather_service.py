import requests
from abc import ABC, abstractmethod
import urllib
import os

from services.ApiError import ApiError
from util import Singleton
from services.preferences import PrefService



class WeatherAdapterModule(ABC):
    @abstractmethod
    def get_current_weather_by_city(self, city:str):
        pass

    @abstractmethod
    def get_weather_forecast_by_city(self, city:str):
        pass

    @abstractmethod
    def get_current_weather_by_coordinates(self, lat, lon):
        pass

    @abstractmethod
    def get_weather_forecast_by_coordinates(self, lat, lon):
        pass

@Singleton
class WeatherAdapterRemote(WeatherAdapterModule):

    def __init__(self):
        self.API_TOKEN = os.environ['OPENWEATHERMAP_API_KEY']
        self.base_url = 'https://api.openweathermap.org/data/2.5'
        self.base_params = {
            'units': 'metric',
            'appid': self.API_TOKEN
        }

    def request(self, url, params):
        url = self.base_url + url
        params = {**params, **self.base_params}
        req = f'{url}?{urllib.parse.urlencode(params)}'

        resp = requests.get(req)
        if resp.status_code != 200:
            raise ApiError((f"GET {req} returned {resp.status_code}:\n"
                            f"{resp.json()['message']}"))
        return resp.json()

    def get_current_weather_by_coordinates(self, lat, lon):
        url = '/weather'
        params = {
            'lat': lat,
            'lon': lon
        }
        return self.request(url, params)

    def get_current_weather_by_city(self, city):
        url = '/weather'
        params = {
            'q': city,
        }
        return self.request(url, params)

    def get_weather_forecast_by_coordinates(self, lat, lon):
        url = '/forecast'
        params = {
            'lat': lat,
            'lon': lon
        }
        return self.request(url, params)

    def get_weather_forecast_by_city(self, city):
        url = '/forecast'
        params = {
            'q': city,
        }
        return self.request(url, params)

@Singleton
class WeatherAdapter:

    remote = None
    weather = []
    weather_forecast = []
    pref = None

    MIN_TEMP = 10.0 #°C
    MAX_WIND = 20.0 #km/h

    def __init__(self, remote:WeatherAdapterModule=None):
        if remote:
            self.remote = remote
        else:
            self.remote =  WeatherAdapterRemote.instance()

        self.pref = PrefService()
        #get_preferences('weather')
        self.MIN_TEMP = self.pref.get_specific_pref('min_temp')
        self.MAX_WIND = self.pref.get_specific_pref('max_wind')

    def set_remote(self, remote:WeatherAdapterModule):
        self.remote = remote

    def update(self, city=None, coordinates:tuple=None):
        if city:
            self.weather = self.remote.get_current_weather_by_city(city)
            self.weather_forecast = self.remote.get_weather_forecast_by_city(city)
        elif coordinates:
            self.weather = self.remote.get_current_weather_by_coordinates(
                *coordinates)
            self.weather_forecast = self.remote.get_weather_forecast_by_coordinates(
                *coordinates)
        else:
            raise Error("Provide either city or coordinates")

    def get_current_temperature(self):
        return float(self.weather['main']['temp'])

    def get_current_weather(self):
        return (self.weather['weather'][0]['main'])

    def get_current_weather_id(self):
        return int(self.weather['weather'][0]['id'])

    def get_current_wind(self):
        return float(self.weather['wind']['speed'])

    def get_forecast_weather(self, hours):
        index = int(hours/3)
        return (self.weather_forecast['list'][index]['weather'][0]['main'])

    def get_forecast_weather_id(self, hours):
        index = int(hours/3)
        return int(self.weather_forecast['list'][index]['weather'][0]['id'])

    def get_forecast_temperature(self, hours):
        index = int(hours/3)
        return float(self.weather_forecast['list'][index]['main']['temp'])

    def get_forecast_wind(self, hours):
        index = int(hours/3)
        return float(self.weather_forecast['list'][index]['wind']['speed'])

    def is_bad_weather(self):
        temp = self.get_current_temperature()
        code = self.get_current_weather_id()
        wind = self.get_current_wind()

        if(((code > 200) & (code  < 799)) | (temp < self.MIN_TEMP) | (wind > self.MAX_WIND)):
            return True
        else:
            return False

    def will_be_bad_weather(self, hours):
        temp = self.get_forecast_temperature(hours)
        code = self.get_forecast_weather_id(hours)
        wind = self.get_forecast_wind(hours)

        if (((code > 200) & (code < 799)) | (temp < self.MIN_TEMP) | (wind > self.MAX_WIND)):
            return True
        else:
            return False

