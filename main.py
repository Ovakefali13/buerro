from services.weatherAPI.weather_service import WeatherAdapter
from usecase import lunch
import json
def main():
    weatherAdapter = WeatherAdapter.instance()
    weatherAdapter.update('Stuttgart')
    print(weatherAdapter.is_bad_weather())
    print(weatherAdapter.will_be_bad_weather(3))
    print(weatherAdapter.will_be_bad_weather(6))
    print(weatherAdapter.will_be_bad_weather(9))
    print(weatherAdapter.weatherForecast)
    print(weatherAdapter.weather)

    l = lunch.Lunchbreak('Stuttgart')


if __name__ == '__main__':
    main()