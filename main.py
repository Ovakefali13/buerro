from services.weatherAPI.weather_service import WeatherAdapter
from usecase import lunch
import json
def main():
    weatherAdapter = WeatherAdapter.instance()
    weatherAdapter.update('Stuttgart')
    print(weatherAdapter.isBadWeather())
    print(weatherAdapter.willBeBadWeather(3))
    print(weatherAdapter.willBeBadWeather(6))
    print(weatherAdapter.willBeBadWeather(9))
    print(weatherAdapter.weatherForecast)
    print(weatherAdapter.weather)

    l = lunch.Lunchbreak('Stuttgart')


if __name__ == '__main__':
    main()