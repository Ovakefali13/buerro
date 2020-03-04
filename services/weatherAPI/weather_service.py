import requests
from services.ApiError import ApiError
from services.Singleton import Singleton
from abc import ABC, abstractmethod
from services.preferences import preferences_adapter


class WeatherAdapterModule(ABC):
    @abstractmethod
    def updateCurrentWeatherByCity(self, city:str):
        pass

    @abstractmethod
    def updateWeatherForecastByCity(self, city:str):
        pass


class WeatherAdapterRemote(WeatherAdapterModule):
    API_TOKEN = '716b047d4b59fba6550709d60756b0fd'
    def updateCurrentWeatherByCity(self, city):
        req = 'https://api.openweathermap.org/data/2.5/weather?q=' +  city + '&units=metric&appid=' + self.API_TOKEN
        print(req)
        resp = requests.get(req)
        if resp.status_code != 200:
            raise ApiError('GET /tasks/ {}'.format(resp.status_code))
            print('Error')
        return resp.json()


    def updateWeatherForecastByCity(self, city):
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
    weatherForecast = []
    PREFS = []

    MIN_TEMP = 10.0 #°C
    MAX_WIND = 20.0 #km/h

    def __init__(self):
        self.remote = WeatherAdapterRemote()
        self.PREFS = preferences_adapter.getWeather()
        self.MIN_TEMP = self.PREFS['min_temp']
        self.MAX_WIND = self.PREFS['max_wind']
        self.update('Stuttgart')

    def setRemote(self, remote:WeatherAdapterModule):
        self.remote = remote

    def update(self, city):
        self.weather = self.updateCurrentWeatherByCity(city)
        self.weatherForecast = self.updateWeatherForecastByCity(city)

    def updateWeatherForecastByCity(self, city:str):
        return self.remote.updateWeatherForecastByCity(city)

    def updateCurrentWeatherByCity(self, city:str):
        return self.remote.updateCurrentWeatherByCity(city)

    def getCurrentTemperature(self):
        return float(self.weather['main']['temp'])

    def getCurrentWeather(self):
        return (self.weather['weather'][0]['main'])

    def getCurrentWeatherID(self):
        return int(self.weather['weather'][0]['id'])

    def getCurrentWind(self):
        return float(self.weather['wind']['speed'])

    def getForecastWeather(self, hours):
        index = int(hours/3)
        return (self.weatherForecast['list'][index]['weather'][0]['main'])

    def getForecastWeatherID(self, hours):
        index = int(hours/3)
        return int(self.weatherForecast['list'][index]['weather'][0]['id'])

    def getForecastTemperature(self, hours):
        index = int(hours/3)
        return float(self.weatherForecast['list'][index]['main']['temp'])

    def getForecastWind(self, hours):
        index = int(hours/3)
        return float(self.weatherForecast['list'][index]['wind']['speed'])

    def isBadWeather(self):
        temp = self.getCurrentTemperature()
        code = self.getCurrentWeatherID()
        wind = self.getCurrentWind()

        print("Code: " + str(code) + "\nTemp: " + str(temp) + "\nWind: " + str(wind) +"\n")

        if(((code > 200) & (code  < 799)) | (temp < self.MIN_TEMP) | (wind > self.MAX_WIND)):
            return True
        else:
            return False


    def willBeBadWeather(self, hours):
        temp = self.getForecastTemperature(hours)
        code = self.getForecastWeatherID(hours)
        wind = self.getForecastWind(hours)

        print("Code: " + str(code) + "\nTemp: " + str(temp) + "\nWind: " + str(wind) + "\n")

        if (((code > 200) & (code < 799)) | (temp < self.MIN_TEMP) | (wind > self.MAX_WIND)):
            return True
        else:
            return False

