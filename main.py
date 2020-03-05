#from services.weatherAPI.weather_service import WeatherAdapter
from services.spoonacular.spoonacular_service import SpoonacularService, SpoonacularJSONRemote
#from usecase import lunch
import json
def main():
    spoonacular_service = SpoonacularService(SpoonacularJSONRemote())
    spoonacular_service.get_recipe_reduced_by_ingredient('pork')
    #weatherAdapter = WeatherAdapter.instance()
    #weatherAdapter.update('Stuttgart')
    #print(weatherAdapter.isBadWeather())
    #print(weatherAdapter.willBeBadWeather(3))
    #print(weatherAdapter.willBeBadWeather(6))
    #print(weatherAdapter.willBeBadWeather(9))
    #print(weatherAdapter.weatherForecast)
    #print(weatherAdapter.weather)


if __name__ == '__main__':
    main()