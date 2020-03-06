#from services.weatherAPI.weather_service import WeatherAdapter
#from services.spoonacular.spoonacular_service import SpoonacularService, SpoonacularJSONRemote
#from usecase import lunch
from services.preferences.pref_service import PrefService, PrefJSONRemote, PrefRemote
from services.spoonacular.spoonacular_service import SpoonacularService, SpoonacularJSONRemote, SpoonacularRemote
from services.todoAPI.todoist_service import TodoistService, TodoistRemote, TodoistJSONRemote
from usecase.cooking import Cooking
import json
def main():
    #spoonacular_service = SpoonacularService(SpoonacularJSONRemote(), 'pork')
    
    #cooking = Cooking('pork')
    #print(cooking.get_response())
    
    todoist = TodoistService(TodoistJSONRemote())
    print(todoist.remote.get_todos(2230686957))
    #print(todoist.get_project_names())
    #print(todoist.get_data_science_id())
    #print(todoist.get_data_science_items())
    #print(todoist.get_shopping_list_id())
    #print(todoist.get_shopping_list_items())
    #print(todoist.get_software_engineering_id())
    #print(todoist.get_software_engineering_items())
    #todoist.set_software_enigneering(['Hello World', 'Test Hello'])
    
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