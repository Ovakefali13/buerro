import requests
from openrouteservice import client
from geocoding import getCoordsFromAddress


class RouteRequest:
    # openroute service
    API_TOKEN = '5b3ce3597851110001cf62488ef50484ef524d228826ecc7b35f5df1'

    def __init__(self):
        print('Init Map Service')

        clnt = client.Client(key=self.API_TOKEN)

        self.PREFS = {
            "profile": "driving-car",
            "preference": "shortest"
        }

        self.request_params = {
            'coordinates': [[12.108259, 54.081919], [12.072063, 54.103684]],
            'format_out': 'json',
            'profile': self.PREFS["profile"],
            'preference': self.PREFS["preference"],
            'instructions': 'false',
            'geometry': 'false',            
        }

        def setRoute(self, start, dest):
            if isinstance(start, list) and isinstance(dest, list):
                self.request_params['coordinates'] = [start, dest]
            elif isinstance (start, str) and isinstance(dest, str):
                self.request_params['coordinates'] = [getCoordsFromAddress(start), getCoordsFromAddress(dest)]
                
        def setTravelMode(self, profile):
            self.request_params['profile'] = profile

        def getRouteInformation(self):
            self.route = clnt.directions(**self.request_params)     

        def printRouteSummary(self):
            distance = self.route['routes'][0]['summary']['distance']
            duration = self.route['routes'][0]['summary']['duration'] 
            print(f"The route is {round(distance / 1000)} km long and takes {round(duration / 60)} minutes.")

        getRouteInformation(self)
        printRouteSummary(self)