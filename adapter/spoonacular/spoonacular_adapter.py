import requests
import json

API_TOKEN = '0a3a6b562932438aaab0cb05460096de'

# searches for the header-data of a recipe with a given ingredient
# return: Id of the first recipe
def searchRecipeBySingleIngredient(ingredient):
    request_string = 'https://api.spoonacular.com/recipes/search?query=' + ingredient + '&number=1&apiKey=' + API_TOKEN
    response_string = requests.get(request_string)
    if response_string.status_code != 200:
        print('Error search by ingredient')
        print(request_string)
    response_json = response_string.json()
    return(response_json['results'][0]['id'])


# searches for the full information of a recipe with a given id
# return: Full json information of a recipe
def searchRecipeDataByID(id):
    request_string = 'https://api.spoonacular.com/recipes/' + str(id) +'/information?apiKey=' + API_TOKEN
    response_string = requests.get(request_string)
    if response_string.status_code != 200:
        print('Error search by ID')
        print(request_string)
    response_json = response_string.json()
    return response_json

# extracts the ingredients out of the recipe json gathered form searchRecipeDataById
# return: list of ingredients and their amount
def getIngredientListById(id):
    recipe_json = searchRecipeDataByID(id)
    ingredient_list = []
    for ingredient in recipe_json['extendedIngredients']:
        ingredient_list.append(ingredient['name'] + ' ' + str(ingredient['amount']) + ' ' + ingredient['unit'])
    print(recipe_json)
    return ingredient_list

# extracts the ingreidients out of a recipe by a given ingedient (first recipe)
# return: Returns ingredient and their amount
def getIngredientListByIngredient(ingredient):
    return getIngredientListById(searchRecipeBySingleIngredient(ingredient))

# returns a full recipe by a given ingredient 
# return: Full information of the first recipe
def getRecipeDataBySingleIngredient(ingredient):
    return searchRecipeDataByID(searchRecipeBySingleIngredient(ingredient))


#Some example running code
# i=0
# for ingredient in getIngredientListByIngredient('pork'):
    # i+=1
    # print(str(i) + ': ' + ingredient)
