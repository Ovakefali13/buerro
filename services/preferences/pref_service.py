import json
import os
from abc import ABC, abstractmethod

class PrefRemote(ABC):
    @abstractmethod
    def load_file(self):
        pass

    @abstractmethod
    def merge_json_files(self, dict1:dict, dict2:dict):
        pass

class PrefJSONRemote(PrefRemote):
    def load_file(self):
        preferences_json = json.load(open('preferences.json'))
        return preferences_json
    def merge_json_files(self, dict1, dict2):
        res = {**dict1, **dict2}
        return res

class PrefService:
    remote = None

    def __init__(self, remote=PrefJSONRemote()):
        self.remote = remote

    def get_preferences(self, key):
        preferences_json = self.remote.load_file()
        return_json = self.remote.merge_json_files(preferences_json["general"], preferences_json[key])
        return return_json
