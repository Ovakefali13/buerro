import json
import os

def loadFile():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'preferences.json')
    preferences_json = json.load(open(filename))
    return preferences_json
def mergerJsonFiles(dict1, dict2): 
    res = {**dict1, **dict2} 
    return res
def getGeneral():
    preferences_json = loadFile()
    return_json = preferences_json["general"]
    return  return_json
def getCooking():
    preferences_json = loadFile()
    return_json = mergerJsonFiles(preferences_json["general"], preferences_json["cooking"])
    return  return_json
def getGithub():
    preferences_json = loadFile()
    return_json = mergerJsonFiles(preferences_json["general"], preferences_json["github"])
    return  return_json
def getWorkday():
    preferences_json = loadFile()
    return_json = mergerJsonFiles(preferences_json["general"], preferences_json["workday"])
    return  return_json
def getTransport():
    preferences_json = loadFile()
    return_json = mergerJsonFiles(preferences_json["general"], preferences_json["transport"])
    return  return_json
def getLunchbreak():
    preferences_json = loadFile()
    return_json = mergerJsonFiles(preferences_json["general"], preferences_json["lunchbreak"])
    return  return_json

# Example Code
# print(getGeneral())
# print(getCooking())
# print(getGithub())
# print(getWorkday())
# print(getTransport())
# print(getLunchbreak())