#from services.weatherAPI.weather_service import WeatherAdapter
#from services.spoonacular.spoonacular_service import SpoonacularService, SpoonacularJSONRemote
#from usecase import lunch
from services.preferences.pref_service import PrefService, PrefJSONRemote, PrefRemote
from services.spoonacular.spoonacular_service import SpoonacularService, SpoonacularJSONRemote, SpoonacularRemote
from usecase.cooking import Cooking
import json
def main():
    #spoonacular_service = SpoonacularService(SpoonacularJSONRemote(), 'pork')
    
    cooking = Cooking('pork')
    print(cooking.get_response())
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