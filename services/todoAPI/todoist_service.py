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

    def get_project_id(self, name):
        response = None
        for project in self.remote.get_projects():
            if project['name'] == name:
                response = project['id']
        return response

    def get_project_items(self, name):
        response = []
        project = self.remote.get_todos(self.get_project_id(name))
        for item in project['items']:
            response.append(item['content'])
        return response
    
    def set_project_todo(self, items, name):
        project_id = self.get_project_id(name)
        return self.remote.set_todos(items, project_id)
