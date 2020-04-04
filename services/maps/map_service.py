from abc import ABC, abstractmethod
from util import Singleton
from urllib.parse import urlencode
from services.preferences import PrefService, PrefJSONRemote
import requests


class MapRemote(ABC):
    @abstractmethod
    def get_route_information(self, start:list, dest:list, travel_mode:str=None):
        pass

@Singleton
class MapJSONRemote(MapRemote):

    def __init__(self):

        pref_service = PrefService(PrefJSONRemote())
        prefs = pref_service.get_preferences('transport')
        self.base_url = 'https://api.openrouteservice.org/v2/directions/'

        self.request_params = {
            'start': None,
            'end': None,
            'profile': 'cycling-regular',
            'api_key': prefs['openrouteserviceAPIKey']
        }


    def __set_route__(self, start:tuple, dest:tuple):
        self.request_params['start'] = start[1], start[0]
        self.request_params['end'] = dest[1], dest[0]


    def __set_travel_mode__(self, profile:dict):
        self.request_params['profile'] = profile


    def get_route_information(self, start:tuple, dest:tuple, travel_mode:str=None):
        self.__set_route__(start, dest)
        if travel_mode:
            self.__set_travel_mode__(travel_mode)
       
        url = self.base_url + f'{self.request_params.get("profile")}?' + urlencode(self.request_params)
        url = url.replace('%28', '')
        url = url.replace('%29', '')
        url = url.replace('%2C', '')
        url = url.replace('+', ',')

        print(url)

        try:
            return requests.get(url)
        except Exception as err:
            raise Exception("Error fetching route information: ", err)
        


@Singleton
class MapService:

    def __init__(self, remote:MapRemote=MapJSONRemote.instance()):
        self.remote = remote


    def get_route_summary(self, start:tuple, dest:tuple, travel_mode:str=None):
        route = self.remote.get_route_information(start, dest, travel_mode).json()
        if route:
            summary = route['features'][0]['properties']['summary']
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
        