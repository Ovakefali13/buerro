import unittest
import os
import json


from .. import YelpService,YelpServiceRemote, YelpServiceModule


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
        print("Mocking remotes...")
        remote = YelpMock()


    yelp_service = None


    def test_get_short_information_of_restaurants(self):
        self.yelp_service = YelpService.instance()
        self.yelp_service.set_remote(self.remote)
        self.yelp_service.set_radius(60, True)
        self.yelp_service.request_businesses(1583160868, 'Jägerstraße 56, 70174 Stuttgart')
        short_information = self.yelp_service.get_short_information_of_restaurants()
        self.assertEquals(short_information[0]['name'], 'Gasthaus Bären')



    def test_get_short_information_of_restaurant(self):
        self.yelp_service = YelpService.instance()
        self.yelp_service.set_remote(self.remote)
        self.yelp_service.set_radius(60, False)
        self.yelp_service.request_businesses(1583160868, 'Jägerstraße 56, 70174 Stuttgart')
        short_information = self.yelp_service.get_short_information_of_restaurants()
        self.yelp_service.request_business(short_information[0]['id'])
        short_info_focused = self.yelp_service.get_business_information()

        self.assertEquals(short_info_focused['name'], 'Gasthaus Bären')


    def test_get_next_business(self):
        self.yelp_service = YelpService.instance()
        self.yelp_service.set_remote(self.remote)
        self.yelp_service.set_radius(60, False)
        self.yelp_service.request_businesses(1583160868, 'Jägerstraße 56, 70174 Stuttgart')

        next_restaurant = self.yelp_service.get_next_business()

        self.assertEquals(next_restaurant['name'], 'Gasthaus Bären')
