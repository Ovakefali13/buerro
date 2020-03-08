import requests
from services.ApiError import ApiError
from services.Singleton import Singleton
from services.preferences import PrefService
from abc import ABC, abstractmethod
import json

class YelpServiceModule(ABC):
    @abstractmethod
    def request_businesses(self, search_param):
        pass

    @abstractmethod
    def request_business(self, id:int):
        pass

class YelpServiceRemote(YelpServiceModule):
    API_TOKEN = PrefService().get_specific_pref('yelpAPIKey')
    headers = {
        'Authorization': 'Bearer %s' % API_TOKEN,
    }

    def request_businesses(self, search_param):
        req = 'https://api.yelp.com/v3/businesses/search'
        response = requests.request('GET', req, headers=self.headers, params=search_param)
        if response.status_code != 200:
            raise ApiError('GET /tasks/ {}'.format(response.status_code))
            print('Error')
        return response.json()

    def request_business(self, id):
        req = 'https://api.yelp.com/v3/businesses/' + id
        response = requests.request('GET', req, headers=self.headers)
        if response.status_code != 200:
            raise ApiError('GET /tasks/ {}'.format(response.status_code))
            print('Error')
        return response.json()


@Singleton
class YelpService:
    remote = None
    restaurants = []
    focused_restaurant = []
    search_params = {}
    pref = None

    def __init__(self):
        self.remote = YelpServiceRemote()
        self.pref = PrefService()

        self.search_params = {
            'term': 'food',
            'location': 'Jägerstraße 56, 70174 Stuttgart',
            'price': self.pref.get_specific_pref('price'),
            'radius': 2000,
            'open_at': 1583160868,
            'limit' : 10,
            'sort_by' : 'distance'
        }

    def set_remote(self, remote):
        self.remote = remote

    def set_location(self, location):
        self.search_params['location'] = location

    def set_time(self, time):
        self.search_params['open_at'] = int(time)

    def set_radius(self, time, isBadWeather):
        if(isBadWeather):
            self.search_params['radius'] = int((self.pref.get_specific_pref('base_radius') + ((time / 10) * self.pref.get_specific_pref('ten_min_radius'))) / 2)
        else:
            self.search_params['radius'] = int(self.pref.get_specific_pref('base_radius') + ((time / 10) * self.pref.get_specific_pref('ten_min_radius')))

    def request_businesses(self, time, location):
        self.set_location(location)
        self.set_time(time)
        self.restaurants = self.remote.request_businesses(self.search_params)

    def request_business(self, id):
        self.focused_restaurant = self.remote.request_business(id)

    def get_business_information(self):
        return self.focused_restaurant

    def get_short_information_of_restaurants(self):
        name_list = []
        for x in self.restaurants['businesses']:
            info = {
                'name' : x['name'],
                'id' : x['id'],
                'price': x['price'],
                'is_closed': x['is_closed'],
                'rating': x['rating'],
                'address': x['location']['address1'] + ', ' + x['location']['zip_code'] + ' ' + x['location']['city'],
                'city' : x['location']['city'],
                'url': x['url'],
            }
            name_list.append(info)
        return name_list


    def get_next_business(self):
        info = {
            'name': self.restaurants['businesses'][0]['name'],
            'id': self.restaurants['businesses'][0]['id'],
            'phone' : self.restaurants['businesses'][0]['phone'],
            'address': self.restaurants['businesses'][0]['location']['address1'] + ', ' + self.restaurants['businesses'][0]['location']['zip_code'] + ' ' + self.restaurants['businesses'][0]['location']['city'],
            'url': self.restaurants['businesses'][0]['url'],
        }
        return info
