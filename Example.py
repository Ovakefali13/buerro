from services.preferences.pref_service import PrefRemote,PrefJSONRemote,PrefService
#from services.spoonacular.spoonacular_service import SpoonacularRemote, SpoonacularJSONRemote, SpoonacularService

i=0
#test = SpoonacularService(SpoonacularJSONRemote())
test1 = PrefService(PrefJSONRemote())

print(test1.get_specific_pref('max_wind'))
#print(test.get_ingredient_list_by_id(111364))