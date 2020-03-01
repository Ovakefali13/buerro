import requests
from Adapter.ApiError import ApiError
from Adapter.Singleton import Singleton

@Singleton
class WeatherAdapter:
    API_TOKEN = '716b047d4b59fba6550709d60756b0fd'
    weather = []
    weatherForecast = []

    MIN_TEMP = 10.0 #°C
    MAX_WIND = 20.0 #km/h
    REFRESH_RATE = 3600 #sec

    def __init__(self):
        self.updateCurrentWeatherByCity('Stuttgart')
        self.updateWeatherForecastByCity('Stuttgart')

    def update(self, city):
        self.updateCurrentWeatherByCity(city)
        self.updateWeatherForecastByCity(city)


    def updateCurrentWeatherByCity(self, city):
        req = 'https://api.openweathermap.org/data/2.5/weather?q=' +  city + '&units=metric&appid=' + self.API_TOKEN
        print(req)
        resp = requests.get(req)
        if resp.status_code != 200:
            raise ApiError('GET /tasks/ {}'.format(resp.status_code))
            print('Error')
        self.weather = resp.json()


    def updateWeatherForecastByCity(self, city):
        req = 'https://api.openweathermap.org/data/2.5/forecast?q=' + city + '&units=metric&appid=' + self.API_TOKEN
        resp = requests.get(req)
        if resp.status_code != 200:
            raise ApiError('GET /tasks/ {}'.format(resp.status_code))
            print('Error')
        self.weatherForecast = resp.json()

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

    #todo forecast data
    #todo wind
    #nur max 1 mal die minute update

#1582826400
#1582837200

#10800
#3 * 3600