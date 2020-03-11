from services.preferences.pref_service import PrefService

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
            'open_at': 1583160868,
            'limit' : 10,
            'sort_by' : 'distance'
        }



    def set_location(self, location):
        self.search_params['location'] = location

    def set_time(self, time):
        self.search_params['open_at'] = int(time)

    def set_radius(self, time, isBadWeather):
        if(isBadWeather):
            self.search_params['radius'] = int((self.pref.get_specific_pref('base_radius') + ((time / 10) * self.pref.get_specific_pref('ten_min_radius'))) / 2)
        else:
            self.search_params['radius'] = int(self.pref.get_specific_pref('base_radius') + ((time / 10) * self.pref.get_specific_pref('ten_min_radius')))

    def get_search_param(self):
        return self.search_params