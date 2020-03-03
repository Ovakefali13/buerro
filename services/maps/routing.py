import requests
from openrouteservice import client
from geocoding import getCoordsFromAddress
from abc import ABC, abstractmethod

class MapRemote(ABC):
    @abstractmethod
    def get_route_information(self, start, dest, travel_mode):
        pass


class MapJSONRemote(MapRemote):
    # openroute service
    API_TOKEN = '5b3ce3597851110001cf62488ef50484ef524d228826ecc7b35f5df1'

    def __init__(self):

        self.clnt = client.Client(key=self.API_TOKEN)
        self.route = None

        self.PREFS = {
            'profile': 'driving-car',
            'preference': 'shortest'
        }

        self.request_params = {
            'coordinates': [[], []],
            'format_out': 'json',
            'profile': self.PREFS['profile'],
            'preference': self.PREFS['preference'],
            'instructions': 'false',
            'geometry': 'false',            
        }

    def __set_route__(self, start, dest):
        if isinstance(start, list) and isinstance(dest, list):
            self.request_params['coordinates'] = [start, dest]
        elif isinstance (start, str) and isinstance(dest, str):
            self.request_params['coordinates'] = [getCoordsFromAddress(start), getCoordsFromAddress(dest)]
            
    def __set_travel_mode__(self, profile):
        self.request_params['profile'] = profile

    def get_route_information(self, start, dest, travel_mode = None):
        self.__set_route__(start, dest)
        if travel_mode:
            self.__set_travel_mode__(travel_mode)
        return self.clnt.directions(**self.request_params)   
        # TODO error handling

    

class MapService:
    remote = None

    def __init__(self, remote):
        self.remote = remote

    def get_route_summary(self, start, dest, travel_mode = None):            
        route = self.remote.get_route_information(start, dest)
        return (route['routes'][0]['summary']['distance'], route['routes'][0]['summary']['duration'] )
        


router = MapService(MapJSONRemote)
print(router.get_route_summary('Rotebühlplatz 41-1, 70178, Stuttgart','Holzgartenstraße 11, 70174 Stuttgart'))
print(router.get_route_summary([9.170963, 48.773563],[9.169989, 48.780834]))