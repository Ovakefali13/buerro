from services.weatherAPI.WeatherAdapter import WeatherAdapter
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


if __name__ == '__main__':
    main()