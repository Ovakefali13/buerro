import json
import os

class PrefJSONRemote():
    def loadFile():
        preferences_json = json.load(open('preferences.json'))
        return preferences_json
    def mergerJsonFiles(dict1, dict2): 
        res = {**dict1, **dict2} 
        return res

class PrefService: 
    remote = None

    def __init__(self, remote):
        self.remote = remote

    def getPreferences(self, key):
        preferences_json = self.remote.loadFile()
        return_json = self.remote.mergerJsonFiles(preferences_json["general"], preferences_json[key])
        return return_json