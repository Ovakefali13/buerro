import unittest
import os
import json
from services.yelp import YelpService,YelpServiceRemote, YelpServiceModule, YelpRequest


class YelpMock(YelpServiceModule):

    def request_businesses(self, search_param):
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, 'mock_yelp_restaurants.json'), 'r') as mockRestaurant_f:
            mockRestaurant = json.load(mockRestaurant_f)
        return mockRestaurant


    def request_business(self, id):
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, 'mock_yelp_restaurants_focused.json'), 'r') as mockFRestaurant_f:
            mockFocusedRestaurant = json.load(mockFRestaurant_f)
        return mockFocusedRestaurant


class TestYelpService(unittest.TestCase):
    if 'DONOTMOCK' in os.environ:
        remote = YelpServiceRemote()
    else:
        print("Mocking remotes... test")
        remote = YelpMock()

    yelp_service = None

    search_params = YelpRequest()
    search_params.set_location('Jägerstraße 56, 70174 Stuttgart')
    search_params.set_time(1583160868)
    search_params.set_radius(60, True)



    def test_get_short_information_of_restaurants(self):
        self.yelp_service = YelpService.instance()
        self.yelp_service.set_remote(self.remote)
        short_information = self.yelp_service.get_short_information_of_restaurants(self.search_params)
        self.assertEquals(short_information[0]['name'], 'Gasthaus Bären')



    def test_get_short_information_of_restaurant(self):
        self.yelp_service = YelpService.instance()
        self.yelp_service.set_remote(self.remote)
        short_information = self.yelp_service.get_short_information_of_restaurants(self.search_params)
        short_info_focused= self.yelp_service.get_business(short_information[0]['id'])
        self.assertEquals(short_info_focused['name'], 'Gasthaus Bären')

    def test_get_businesses(self):
        self.yelp_service = YelpService.instance()
        self.yelp_service.set_remote(self.remote)
        information = self.yelp_service.get_businesses(self.search_params)
        self.assertEquals(information['businesses'][0]['name'], 'Gasthaus Bären')


    def test_get_next_business(self):
        self.yelp_service = YelpService.instance()
        self.yelp_service.set_remote(self.remote)
        next_restaurant = self.yelp_service.get_next_business(self.search_params)
        self.assertEquals(next_restaurant['name'], 'Gasthaus Bären')
