import json
from abc import ABC, abstractmethod
from ..preferences.pref_service import PrefService, PrefJSONRemote, PrefRemote
import todoist

class TodoistRemote(ABC):
    @abstractmethod
    def get_projects(self):
        pass

    @abstractmethod
    def get_todos(self):
        pass

    @abstractmethod
    def set_todos(self):
        pass

class TodoistJSONRemote(TodoistRemote):
    api_token = ''
    pref_service = PrefService(PrefJSONRemote())
    api = None

    def __init__(self):
        pref_json = self.pref_service.get_preferences("cooking")
        self.api_token = pref_json['todoistAPIKey']
        self.api = todoist.TodoistAPI(self.api_token)
        self.api.sync()

    def get_projects(self):
        return self.api.state['projects']

    def get_todos(self, project_id):
        return self.api.projects.get_data(project_id)
    
    def set_todos(self, items, p_id):
        for item in items:
            self.api.items.add(item, project_id=p_id)
        self.api.commit()

class TodoistService:
    remote = None

    def __init__(self, remote):
        self.remote = remote
    
    def get_project_names(self):
        response = []
        for project in self.remote.get_projects():
            response.append(project['name'])
        return response

    def get_shopping_list_id(self):
        response = None
        for project in self.remote.get_projects():
            if project['name'] == 'Shopping List':
                response = project['id']
        return response

    def get_shopping_list_items(self):
        response = []
        project = self.remote.get_todos(self.get_shopping_list_id())
        for item in project['items']:
            response.append(item['content'])
        return response

    def get_software_engineering_id(self):
        response = None
        for project in self.remote.get_projects():
            if project['name'] == 'Software Engineering':
                response = project['id']
        return response

    def get_software_engineering_items(self):
        response = []
        project = self.remote.get_todos(self.get_software_engineering_id())
        for item in project['items']:
            response.append(item['content'])
        return response

    def get_data_science_id(self):
        response = None
        for project in self.remote.get_projects():
            if project['name'] == 'Data Science':
                response = project['id']
        return response

    def get_data_science_items(self):
        response = []
        project = self.remote.get_todos(self.get_data_science_id())
        for item in project['items']:
            response.append(item['content'])
        return response
    
    def set_shopping_list(self, items):
        project_id = self.get_shopping_list_id()
        return self.remote.set_todos(items, project_id)
    
    def set_data_science(self, items):
        project_id = self.get_data_science_id()
        return self.remote.set_todos(items, project_id)
    
    def set_software_enigneering(self, items):
        project_id = self.get_software_engineering_id()
        return self.remote.set_todos(items, project_id)
