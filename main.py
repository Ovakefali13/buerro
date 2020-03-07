from services.preferences.pref_service import PrefService, PrefJSONRemote, PrefRemote
from services.spoonacular.spoonacular_service import SpoonacularService, SpoonacularJSONRemote, SpoonacularRemote
from services.todoAPI.todoist_service import TodoistService, TodoistRemote, TodoistJSONRemote
from usecase.cooking import Cooking
import json
def main():
    l = lunch.Lunchbreak('Stuttgart')
    t =  todoist = TodoistService(TodoistJSONRemote())
    s = spoonacular_service = SpoonacularService(SpoonacularJSONRemote(), 'pork')

if __name__ == '__main__':
    main()