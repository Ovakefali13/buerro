import json
from abc import ABC, abstractmethod
from ..preferences.pref_service import PrefService, PrefJSONRemote, PrefRemote

class TodoistRemote(ABC):
    @abstractmethod
    def get_todos(self):
        pass

    @abstractmethod
    def get_search_options(self):
        pass

    @abstractmethod
    def set_todos(self):
        pass

class TodoistJSONRemote(TodoistRemote):
    base_url = ''
    api_token = ''
    pref_service = PrefService(PrefJSONRemote())

    def __init__(self):
        pref_json = self.pref_service.get_preferences("cooking")
        self.api_token = pref_json['todoistAPIKey']

    def get_todos(self):
        return "Hello World"

    def get_search_options(self):
        search_options = 'includeIngredients=' + ''
        search_options += '&diet=' + ''
        search_options += '&maxReadyTime=' + ''
        search_options += '&apiKey=' + ''
        return search_options
    
    def set_todos(self):
        return "Hello World"

class TodoistService:
    remote = None

    def __init__(self, remote):
        self.remote = remote