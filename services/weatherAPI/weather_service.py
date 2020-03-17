import requests
from services.ApiError import ApiError
from services.singleton import Singleton
from abc import ABC, abstractmethod
from services.preferences import PrefService


class WeatherAdapterModule(ABC):
    @abstractmethod
    def update_current_weather_by_city(self, city:str):
        pass

    @abstractmethod
    def update_weather_forecast_by_city(self, city:str):
        pass


class WeatherAdapterRemote(WeatherAdapterModule):
    API_TOKEN = PrefService().get_specific_pref('openWeatherMapAPIKey')

    def update_current_weather_by_city(self, city):
        req = 'https://api.openweathermap.org/data/2.5/weather?q=' +  city + '&units=metric&appid=' + self.API_TOKEN
        resp = requests.get(req)
        if resp.status_code != 200:
            raise ApiError('GET /tasks/ {}'.format(resp.status_code))
            print('Error')
        return resp.json()


    def update_weather_forecast_by_city(self, city):
        req = 'https://api.openweathermap.org/data/2.5/forecast?q=' + city + '&units=metric&appid=' + self.API_TOKEN
        resp = requests.get(req)
        if resp.status_code != 200:
            raise ApiError('GET /tasks/ {}'.format(resp.status_code))
            print('Error')
        return resp.json()

@Singleton
class WeatherAdapter:

    remote = None
    weather = []
    weather_forecast = []
    pref = None

    MIN_TEMP = 10.0 #°C
    MAX_WIND = 20.0 #km/h

    def __init__(self):
        self.remote = WeatherAdapterRemote()
        self.pref = PrefService()
        #get_preferences('weather')
        self.MIN_TEMP = self.pref.get_specific_pref('min_temp')
        self.MAX_WIND = self.pref.get_specific_pref('max_wind')
        self.update('Stuttgart')

    def set_remote(self, remote:WeatherAdapterModule):
        self.remote = remote

    def update(self, city):
        self.weather = self.update_current_weather_by_city(city)
        self.weather_forecast = self.update_weather_forecast_by_city(city)

    def update_weather_forecast_by_city(self, city:str):
        return self.remote.update_weather_forecast_by_city(city)

    def update_current_weather_by_city(self, city:str):
        return self.remote.update_current_weather_by_city(city)

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

