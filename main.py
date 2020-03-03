from services.weatherAPI.WeatherAdapter import WeatherAdapter
def main():
    weatherAdapter = WeatherAdapter.instance()
    weatherAdapter.update('Stuttgart')
    print(weatherAdapter.isBadWeather())
    print(weatherAdapter.willBeBadWeather(3))
    print(weatherAdapter.willBeBadWeather(6))
    print(weatherAdapter.willBeBadWeather(9))


if __name__ == '__main__':
    main()