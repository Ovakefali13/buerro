import unittest
import os
import json
from services.yelp import YelpService,YelpServiceRemote, YelpServiceModule, YelpRequest
from datetime import datetime

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

    @classmethod
    def setUpClass(self):
        self.remote = None
        if 'DONOTMOCK' in os.environ:
            self.remote = YelpServiceRemote()
        else:
            print("Mocking remotes...")
            self.remote = YelpMock()

        self.search_params = YelpRequest()
        self.search_params.set_location('Jägerstraße 56, 70174 Stuttgart')

        mock_request_time = datetime.timestamp(datetime.now().replace(hour=12, minute=0, second=0, microsecond=0))
        self.search_params.set_time(mock_request_time)

        self.search_params.set_radius(120, True)

    @classmethod
    def setUp(self):
        self.yelp_service = YelpService.instance()
        self.yelp_service.set_remote(self.remote)

    def test_get_short_information_of_restaurants(self):
        short_information = self.yelp_service.get_short_information_of_restaurants(self.search_params)
        self.assertIsInstance(short_information[0]['name'], str)

    def test_get_short_information_of_restaurant(self):
        short_information = self.yelp_service.get_short_information_of_restaurants(self.search_params)
        short_info_focused= self.yelp_service.get_business(short_information[0]['id'])
        self.assertIsInstance(short_info_focused['name'], str)

    def test_get_businesses(self):
        information = self.yelp_service.get_businesses(self.search_params)
        self.assertIsInstance(information['businesses'][0]['name'], str)

    def test_get_next_business(self):
        next_restaurant = self.yelp_service.get_next_business(self.search_params)
        self.assertIsInstance(next_restaurant['name'], str)
