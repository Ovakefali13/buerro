import requests
from services.ApiError import ApiError
from services.Singleton import Singleton
from services.preferences import preferences_adapter
from abc import ABC, abstractmethod

class YelpServiceModule(ABC):
    @abstractmethod
    def requestBusinesses(self):
        pass

    @abstractmethod
    def requestBusiness(self, id:int):
        pass

class YelpServiceRemote(YelpServiceModule):
    def requestBusinesses(self):
        req = 'https://api.yelp.com/v3/businesses/search'
        response = requests.request('GET', req, headers=self.headers, params=self.searchParams)
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
    CLIENT_ID = 'A5Kch4F4A_1vSRVEEkgMnw'
    API_TOKEN = 'AA4LFvZbdhM3IgESoZAlBJSpsvKSHzVbYmpdbo7hehlsrBY-ZdzZIo9ZT7-hRSnlD3RLwnFR8sakmKVTb3xLcrYB3FM6j13KoOiEPh28uGESSgIPFbHdffk4UMZcXnYx'
    restaurants = []
    focusedRestaurant = []
    searchParams = {}
    headers = {}
    PREFS = {}

    def __init__(self):
        self.remote = YelpServiceRemote
        print('Init Yelp Service')
        self.headers = {
            'Authorization': 'Bearer %s' % self.API_TOKEN,
        }
        self.PREFS = preferences_adapter.getLunchbreak()
        print(self.PREFS)

        self.searchParams = {
            'term': 'food',
            'location': 'Jägerstraße 56, 70174 Stuttgart',
            'price': self.PREFS['price'],
            'radius': 2000,
            'open_at': 1583160868,
            'limit' : 10,
            'sort_by' : 'distance'
        }

    def setLocation(self, location):
        self.searchParams['location'] = location

    def setTime(self, time):
        self.searchParams['open_at'] = int(time)

    def setRadius(self, time, isBadWeather):
        if(isBadWeather):
            self.searchParams['radius'] = int((self.PREFS['base_radius'] + ((time/10) * self.PREFS['ten_min_radius'])) / 2)
        else:
            self.searchParams['radius'] = int(self.PREFS['base_radius'] + ((time/10) * self.PREFS['ten_min_radius']))

    def requestBusinesses(self, time, location):
        self.setLocation(location)
        self.setTime(time)
        self.requestBusinesses()

    def requestBusinesses(self):
        self.restaurants = self.remote.requestBusinesses()

    def requestBusiness(self, id):
        self.focusedRestaurant = self.remote.requestBusiness(id)


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

    def getShortInformationOfRestaurant(self, num):
        shortList = {
            'id' : self.restaurants['businesses'][num]['id'],
            'name': self.restaurants['businesses'][num]['name'],
            'price': self.restaurants['businesses'][num]['price'],
            'is_closed': self.restaurants['businesses'][num]['is_closed'],
            'rating': self.restaurants['businesses'][num]['rating'],
            'location': self.restaurants['businesses'][num]['location'],
            'url': self.restaurants['businesses'][num]['url'],
        }

        return shortList

    def printBusinessNames(self):
        for x in self.restaurants['businesses']:
            print(x['id'] + '\t' + x['name'] + '\t' + x['price'] + '\t' + str(x['is_closed']) + '\t' + str(x['rating']) + '\t' + str(x['location'])  + '\t' + x['url'] )

