import requests
from services.ApiError import ApiError
from services.Singleton import Singleton
from services.preferences import PrefService
from abc import ABC, abstractmethod
import json

class YelpServiceModule(ABC):
    @abstractmethod
    def requestBusinesses(self):
        pass

    @abstractmethod
    def requestBusiness(self, id:int):
        pass

class YelpServiceRemote(YelpServiceModule):
    CLIENT_ID = 'A5Kch4F4A_1vSRVEEkgMnw'
    API_TOKEN = 'AA4LFvZbdhM3IgESoZAlBJSpsvKSHzVbYmpdbo7hehlsrBY-ZdzZIo9ZT7-hRSnlD3RLwnFR8sakmKVTb3xLcrYB3FM6j13KoOiEPh28uGESSgIPFbHdffk4UMZcXnYx'
    headers = {
        'Authorization': 'Bearer %s' % API_TOKEN,
    }

    def requestBusinesses(self, searchParam):
        req = 'https://api.yelp.com/v3/businesses/search'
        response = requests.request('GET', req, headers=self.headers, params=searchParam)
        if response.status_code != 200:
            raise ApiError('GET /tasks/ {}'.format(response.status_code))
            print('Error')
        return response.json()

    def requestBusiness(self, id):
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
    focusedRestaurant = []
    searchParams = {}
    pref = None

    def __init__(self):
        self.remote = YelpServiceRemote()
        print('Init Yelp Service')
        self.pref = PrefService()
        print(self.pref.get_preferences('lunchbreak'))

        self.searchParams = {
            'term': 'food',
            'location': 'Jägerstraße 56, 70174 Stuttgart',
            'price': self.pref.get_specific_pref('price'),
            'radius': 2000,
            'open_at': 1583160868,
            'limit' : 10,
            'sort_by' : 'distance'
        }

    def setRemote(self, remote):
        self.remote = remote

    def setLocation(self, location):
        self.searchParams['location'] = location

    def setTime(self, time):
        self.searchParams['open_at'] = int(time)

    def setRadius(self, time, isBadWeather):
        if(isBadWeather):
            self.searchParams['radius'] = int((self.pref.get_specific_pref('base_radius') + ((time/10) * self.pref.get_specific_pref('ten_min_radius'))) / 2)
        else:
            self.searchParams['radius'] = int(self.pref.get_specific_pref('base_radius') + ((time/10) * self.pref.get_specific_pref('ten_min_radius')))

    def requestBusinesses(self, time, location):
        self.setLocation(location)
        self.setTime(time)
        self.requestBusinesses()

    def requestBusinesses(self):
        self.restaurants = self.remote.requestBusinesses(self.searchParams)

    def requestBusiness(self, id):
        self.focusedRestaurant = self.remote.requestBusiness(id)

    def getBusinessInformation(self):
        return self.focusedRestaurant

    def getShortInformationOfRestaurants(self):
        nameList = []
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
            nameList.append(info)
        return nameList


    def getNextBusiness(self):
        info = {
            'name': self.restaurants['businesses'][0]['name'],
            'id': self.restaurants['businesses'][0]['id'],
            'phone' : self.restaurants['businesses'][0]['phone'],
            'address': self.restaurants['businesses'][0]['location']['address1'] + ', ' + self.restaurants['businesses'][0]['location']['zip_code'] + ' ' + self.restaurants['businesses'][0]['location']['city'],
            'url': self.restaurants['businesses'][0]['url'],
        }
        return info
