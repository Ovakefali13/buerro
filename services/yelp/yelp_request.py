from services.preferences.pref_service import PrefService
from datetime import datetime

class YelpRequest:

    search_params = {}
    pref = None

    def __init__(self):
        self.pref = PrefService()
        self.search_params = {
            'term': 'food',
            'location' : 'Jägerstraße 56, 70174 Stuttgart',
            'price': self.pref.get_specific_pref('price'),
            'radius': 2000,
            'open_at': datetime.timestamp(datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)),
            'limit' : 10,
            'sort_by' : 'distance'
        }



    def set_location(self, location):
        self.search_params['location'] = location
        self.search_params.pop('latitude', None)
        self.search_params.pop('longitude', None)

    def set_coordinates(self, coords:list):
        self.search_params['latitude'] = coords[0]
        self.search_params['longitude'] = coords[1]
        self.search_params.pop('location', None)

    def set_time(self, time):
        self.search_params['open_at'] = int(time)

    #Set radius in accordance to weather and time available
    def set_radius(self, time, isBadWeather):
        if(isBadWeather):
            self.search_params['radius'] = int((self.pref.get_specific_pref('base_radius') + ((time / 10) * self.pref.get_specific_pref('ten_min_radius'))) / 2)
        else:
            self.search_params['radius'] = int(self.pref.get_specific_pref('base_radius') + ((time / 10) * self.pref.get_specific_pref('ten_min_radius')))

    #Set radius in meter
    def set_radius_im_meters(self, meter):
        self.search_params['radius'] = meter


    def get_search_param(self):
        return self.search_params