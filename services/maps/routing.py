import requests
from openrouteservice import client
from geocoding import getCoordsFromAddress

class RouteRequest:
    # openroute service
    API_TOKEN = '5b3ce3597851110001cf62488ef50484ef524d228826ecc7b35f5df1'

    def __init__(self):
        print('Init Map Service')

        self.clnt = client.Client(key=self.API_TOKEN)
        self.route = None

        self.PREFS = {
            'profile': 'driving-car',
            'preference': 'shortest'
        }

        self.request_params = {
            'coordinates': [[12.108259, 54.081919], [12.072063, 54.103684]],
            'format_out': 'json',
            'profile': self.PREFS['profile'],
            'preference': self.PREFS['preference'],
            'instructions': 'false',
            'geometry': 'false',            
        }

    def __set_route(self, start, dest):
        if isinstance(start, list) and isinstance(dest, list):
            self.request_params['coordinates'] = [start, dest]
        elif isinstance (start, str) and isinstance(dest, str):
            self.request_params['coordinates'] = [getCoordsFromAddress(start), getCoordsFromAddress(dest)]
            
    def __load_route_information(self, start, dest):
        self.__set_route(start, dest)
        self.route = self.clnt.directions(**self.request_params)   

    def __set_travel_mode(self, profile):
        self.request_params['profile'] = profile

    def get_route_summary(self, start, dest, travel_mode = None):
        if travel_mode:
            self.__set_travel_mode(travel_mode)      
        self.__load_route_information(start, dest)
        return (self.route['routes'][0]['summary']['distance'], self.route['routes'][0]['summary']['duration'] )
        


router = RouteRequest()
print(router.get_route_summary('Rotebühlplatz 41-1, 70178, Stuttgart','Holzgartenstraße 11, 70174 Stuttgart'))
print(router.get_route_summary([9.170963, 48.773563],[9.169989, 48.780834]))