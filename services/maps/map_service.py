from openrouteservice import client
from abc import ABC, abstractmethod
import os

from util import Singleton
from services.preferences import PrefService, PrefJSONRemote


class MapRemote(ABC):
    @abstractmethod
    def get_route_information(self, start:list, dest:list, travel_mode:str=None):
        pass

@Singleton
class MapJSONRemote(MapRemote):

    def __init__(self):

        pref_service = PrefService(PrefJSONRemote())
        prefs = pref_service.get_preferences('transport')
        self.clnt = client.Client(key=os.environ['OPENROUTESERVICE_API_KEY'])

        self.request_params = {
            'coordinates': [(), ()],
            'format_out': 'json',
            'profile': 'cycling-regular',
            'preference': 'shortest',
            'instructions': 'false',
            'geometry': 'false',
        }


    def __set_route__(self, start:tuple, dest:tuple):
        self.request_params['coordinates'] = [(start[1], start[0]), (dest[1],dest[0])]


    def __set_travel_mode__(self, profile:dict):
        self.request_params['profile'] = profile


    def get_route_information(self, start:tuple, dest:tuple, travel_mode:str=None):
        self.__set_route__(start, dest)
        if travel_mode:
            self.__set_travel_mode__(travel_mode)
        try:
            return self.clnt.directions(**self.request_params)
        except:
            return None
        


@Singleton
class MapService:

    def __init__(self, remote:MapRemote=MapJSONRemote.instance()):
        self.remote = remote


    def get_route_summary(self, start:tuple, dest:tuple, travel_mode:str=None):
        route = self.remote.get_route_information(start, dest, travel_mode)
        if route:
            summary = route['routes'][0]['summary']
            coords = route['metadata']['query']['coordinates']

            return {'start': (coords[0][1], coords[0][0]),
                    'dest': (coords[1][1], coords[1][0]),
                    'distance': summary['distance'],
                    'duration':  summary['duration']}

    def get_route_link(self, start:tuple, dest:tuple, mode:str='cycling'):

        if mode == 'car':
            mode = 0
        elif mode == 'cycling':
            mode = 1
        elif mode == 'walking':
            mode = 2
        return f'https://routing.openstreetmap.de/?loc={start[0]}%2C{start[1]}&loc={dest[0]}%2C{dest[1]}&hl=en&srv={mode}'
        
